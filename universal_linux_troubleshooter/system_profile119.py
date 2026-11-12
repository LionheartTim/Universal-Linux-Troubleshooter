"""Local, shared, privacy-limited system inventory (v119).

First launch obtains a full offline baseline; later scans refresh only changed or
expired areas.  This module has NO repair, privilege, shell or network API.
A snapshot is context, NEVER proof that current hardware is healthy and NEVER
an authorization for a modifying command or optional external request.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import platform
import shutil
import stat
import tempfile
import time

from .flatpak_host138 import view_path, in_flatpak
from .diagnostics import READY_CHECKS
from .diagnostics.bridge import DiagnosticBridge, LocalHost
from .diagnostics.plan import complete_system_plan
from .results import DiagnosticResult, ResultStatus

SCHEMA = 1
LOCAL_PLAN = complete_system_plan(READY_CHECKS)
LOCAL_IDS = frozenset(f'{area}/{check}' for area, check in LOCAL_PLAN)
# Never persist raw logs, IPs, hardware serials, usernames, paths or command
# output. Only these short, curated diagnoses are stored; everything else
# stores the reviewed check name/status, not possibly identifying content.
SAFE_SUMMARY = frozenset({
    'graphics/gpu', 'graphics/display', 'graphics/render', 'storage/drives',
    'storage/space', 'hardware/memory', 'network/adapter', 'audio/bluetooth',
    'audio/audio_devices', 'system/boot', 'system/updates',
})
AREA_TTLS = {
    'network': 10 * 60, 'audio': 15 * 60, 'applications': 15 * 60,
    'system': 30 * 60, 'storage': 30 * 60, 'graphics': 30 * 60,
    'hardware': 30 * 60, 'virtualization': 30 * 60,
}
# These paths only provide coarse change hints.  They are NOT searched for
# personal content. File metadata and limited interface state are hashed; raw
# fingerprints are not placed on disk. Polling catches missed Qt watch events.
WATCH_PATHS = {
    'network': ('/sys/class/net', '/etc/NetworkManager/system-connections', '/etc/resolv.conf'),
    'audio': ('/sys/class/sound', '/sys/class/bluetooth', '/etc/pipewire'),
    'applications': ('~/Applications', '~/.local/bin', '/var/lib/dpkg/status', '/var/lib/pacman/local',
                     '/var/lib/rpm', '/usr/lib/sysimage/rpm', '/var/lib/snapd/snaps',
                     '/var/lib/flatpak/app', '~/.local/share/flatpak/app',
                     '/etc/apk/world', '/lib/apk/db/installed',
                     '/usr/share/applications', '/usr/local/share/applications',
                     '/var/lib/flatpak/exports/share/applications',
                     '~/.local/share/applications', '~/.config/mimeapps.list',
                     '~/.local/share/applications/mimeapps.list', '~/.config/kdeglobals',
                     '~/.local/share/flatpak/exports/share/applications',
                     '/var/lib/flatpak/app', '~/.local/share/flatpak/app'),
    'system': ('/etc/os-release', '/run/ostree-booted', '/var/lib/rpm', '/usr/lib/os-release'),
    'storage': ('/sys/class/block', '/etc/fstab'),
    'graphics': ('/sys/class/drm', '/sys/class/backlight'),
    'hardware': ('/sys/class/power_supply', '/sys/class/thermal', '/sys/devices/system/memory'),
    'virtualization': ('/dev/kvm', '/etc/libvirt'),
}


def readable_profile_watch_paths(paths_by_area=None) -> tuple[str, ...]:
    """Return safe, accessible Qt watch targets without requesting privileges.

    Qt's Linux watcher calls inotify_add_watch(), which can emit a terminal
    permission warning on a directory that exists but cannot be read (for
    example /etc/libvirt on some distros). An inaccessible watch is optional:
    signatures() and the timed profile refresh still run independently.
    Do not modify permissions, follow arbitrary directory contents or hide
    failures from actual diagnostic probes.
    """
    groups = WATCH_PATHS if paths_by_area is None else paths_by_area
    accepted = set()
    for paths in groups.values():
        for raw in paths:
            path = view_path(raw)
            try:
                if not path.exists():
                    continue
                access = os.R_OK | os.X_OK if path.is_dir() else os.R_OK
                if not os.access(path, access):
                    continue
                accepted.add(str(path))
            except (OSError, PermissionError):
                # Permission-denied paths must not be passed to Qt inotify.
                continue
    return tuple(sorted(accepted))


def _state_path() -> Path:
    base = os.environ.get('XDG_STATE_HOME', '')
    home = Path.home()
    root = Path(base) if base and Path(base).is_absolute() else home / '.local' / 'state'
    return root / 'universal-linux-troubleshooter' / 'system-profile.json'


def _stat_parts(path: Path) -> tuple:
    try:
        # lstat rather than following symlink (avoid exposing target paths).
        s = view_path(path).lstat()
        return (s.st_mode & 0o170000, s.st_mtime_ns, s.st_size, s.st_ino)
    except OSError:
        return (0,)


def signatures(*, host=None) -> dict[str, str]:
    """Bounded, read-only hints: no scanning of arbitrary home directories."""
    out = {}
    for area, paths in WATCH_PATHS.items():
        parts = [(_path, _stat_parts(Path(_path).expanduser())) for _path in paths]
        if area == 'network':
            # A connection can change carrier without changing a directory mtime.
            root = view_path('/sys/class/net')
            try:
                names = sorted(p.name for p in root.iterdir())[:64]
                for name in names:
                    if re.fullmatch(r'[A-Za-z0-9_.:@-]{1,64}', name):
                        p = root / name / 'operstate'
                        try:
                            parts.append((name, p.read_text()[:32].strip()))
                        except OSError:
                            parts.append((name, 'unknown'))
            except OSError:
                pass
        digest = hashlib.sha256(repr(parts).encode('utf-8')).hexdigest()
        out[area] = digest
    return out


def _safe_summary(key: str, text: str) -> str:
    if key not in SAFE_SUMMARY or not isinstance(text, str):
        return ''
    candidate = ' '.join(text.split())[:220]
    # Identifiers are not needed in persistent profile details. We prefer
    # omission over pretending redaction is perfect.
    if re.search(r'(?i)(?:/home/|/dev/|\b(?:\d{1,3}\.){3}\d{1,3}\b|'
                 r'\b[0-9a-f]{2}(?::[0-9a-f]{2}){5}\b|serial|uuid|hostname|user:)', candidate):
        return ''
    return candidate


def os_facts() -> dict[str, str]:
    """Small host OS/desktop inventory (no commands, no login information)."""
    result = {}
    try:
        source = view_path('/etc/os-release')
        if not source.exists():
            source = view_path('/usr/lib/os-release')
        lines = source.read_text(encoding='utf-8', errors='replace')[:16384].splitlines()
        for line in lines:
            if not line or '=' not in line:
                continue
            k, v = line.split('=', 1)
            if k in {'ID', 'PRETTY_NAME', 'VERSION_ID'}:
                value = v.strip().strip('"\'')[:120]
                if re.fullmatch(r'[A-Za-z0-9 ._+()/-]{1,120}', value):
                    result[{'ID':'distro_id', 'PRETTY_NAME':'distro_name',
                            'VERSION_ID':'distro_version'}[k]] = value
    except OSError:
        pass
    kernel = platform.release()[:80]
    if re.fullmatch(r'[A-Za-z0-9._+-]{1,80}', kernel):
        result['kernel'] = kernel
    for env, key in (('XDG_CURRENT_DESKTOP','desktop'), ('XDG_SESSION_TYPE','session')):
        value = os.getenv(env, '')[:80]
        if re.fullmatch(r'[A-Za-z0-9_+:-]{1,80}', value):
            result[key] = value
    tools = [name for name in ('flatpak','rpm','rpm-ostree','dnf','zypper','dpkg',
                               'dpkg-query','apt','pacman','snap','apk','xbps-query','nix')
             if shutil.which(name)] if not in_flatpak() else []
    result['package_tools'] = ','.join(tools) if not in_flatpak() else 'checked separately on host'
    return result


def scan_baseline(checks=LOCAL_PLAN, *, bridge=None):
    """Run only fixed, registered LOCAL checks. Safe to call in background."""
    runner = bridge if bridge is not None else DiagnosticBridge(allow_network=False)
    collected = []
    for area, check in checks:
        if (area, check) not in LOCAL_PLAN:
            raise ValueError('Unapproved or external inventory check')
        collected.append(runner.run_check(area, check))
    return tuple(collected)


def browser_facts(*, host=None) -> dict[str, object]:
    """Identify application defaults without opening apps or browser profiles.

    Read only known MIME handlers and Flatpak app IDs through fixed host
    commands. Desktop IDs are configuration, NOT proof of app functionality.
    """
    from .diagnostics.browser_inventory119 import probe_browser_inventory119
    from .diagnostics.bridge import LocalHost as _LocalHost
    runner = host if host is not None else _LocalHost()
    result = probe_browser_inventory119(runner)
    facts = {}
    for entry in result.evidence:
        if not entry.startswith('FACT:') or '=' not in entry:
            continue
        key, val = entry[5:].split('=', 1)
        if key in {'browser_default', 'browser_handlers', 'browser_launcher', 'browser_flatpak_apps', 'browser_package_sources'}:
            if len(val) <= 160 and re.fullmatch(r'[A-Za-z0-9_|-]+', val):
                facts[key] = val
    # Additional default applications are useful for every diagnosis area.
    # Store only strict desktop IDs, never paths or config-file contents.
    mime_types = {
        'html': 'text/html', 'pdf': 'application/pdf',
        'images': 'image/png', 'text': 'text/plain',
    }
    for label, mime in mime_types.items():
        try:
            output = runner.command(('xdg-mime', 'query', 'default', mime))
            raw = output.out.strip()
            if (output.code == 0 and not output.truncated
                    and re.fullmatch(r'[A-Za-z0-9_.+-]{1,200}\.desktop', raw)):
                facts['default_' + label] = raw[:-8]
        except (OSError, TypeError, ValueError, AttributeError):
            continue
    # Installed Flatpak IDs are locally available without listing arbitrary
    # profile files or making requests to package stores.
    app_ids = set()
    sources_ok = 0
    for args in (('flatpak','list','--app','--user','--columns=application'),
                 ('flatpak','list','--app','--system','--columns=application')):
        try:
            output = runner.command(args)
            if output.code != 0 or output.truncated or len(output.out) > 131072:
                continue
            sources_ok += 1
            for line in output.out.splitlines():
                app = line.strip()
                if re.fullmatch(r'[A-Za-z0-9_.-]{2,150}', app):
                    app_ids.add(app)
        except (OSError, TypeError, ValueError, AttributeError):
            continue
    facts['installed_flatpak_count'] = str(len(app_ids)) if sources_ok == 2 else 'unknown'
    # A failed listing is not proof of no installed applications.
    facts['installed_flatpaks'] = '|'.join(sorted(app_ids)[:320]) if sources_ok == 2 else ''
    return facts


class SystemProfile:
    """A single shared repository for AI and Manual Diagnostics.

    Read-only regarding the host; the only write is its own private app-state
    JSON. Invalid/older profiles cause a rescan, never guessed observations.
    """
    def __init__(self, path: Path | None = None, *, clock=None, signature_source=None):
        self.path = Path(path) if path is not None else _state_path()
        self.clock = clock if clock is not None else time.time
        self.signature_source = signature_source or signatures
        self.data: dict = {'schema': SCHEMA, 'complete': False, 'checks': {},
                           'browser': {}, 'os': {}, 'packages': {},
                           'signatures': {}, 'area_updated': {}}
        self._load()

    def _load(self):
        try:
            info = self.path.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536 or info.st_size == 0:
                return
            # Never follow an attacker-controlled symlink.
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if (not isinstance(raw, dict) or raw.get('schema') != SCHEMA
                    or not isinstance(raw.get('checks'), dict)
                    or not isinstance(raw.get('area_updated'), dict)
                    or not isinstance(raw.get('signatures'), dict)
                    or not isinstance(raw.get('browser'), dict)
                    or not isinstance(raw.get('os'), dict)):
                return
            checks = raw['checks']
            if len(checks) > len(LOCAL_PLAN) or any(k not in LOCAL_IDS for k in checks):
                return
            if any(not isinstance(v, dict) or
                   v.get('status') not in {x.value for x in ResultStatus} or
                   not isinstance(v.get('summary'), str) or len(v['summary']) > 220
                   for v in checks.values()):
                return
            browser = raw['browser']
            allowed_browser_keys = {'browser_default', 'browser_handlers', 'browser_launcher',
                                    'browser_flatpak_apps', 'browser_package_sources', 'default_html', 'default_pdf',
                                    'default_images', 'default_text', 'installed_flatpak_count',
                                    'installed_flatpaks'}
            if (any(k not in allowed_browser_keys or not isinstance(v, str)
                    or len(v) > (32000 if k == 'installed_flatpaks' else 160)
                    or not re.fullmatch(r'[A-Za-z0-9_.|+-]*', v)
                    for k, v in browser.items())
                    or any(k not in WATCH_PATHS for k in raw['signatures'])
                    or any(k not in WATCH_PATHS for k in raw['area_updated'])):
                return
            osdata = raw['os']
            if any(k not in {'distro_id','distro_name','distro_version','kernel',
                             'desktop','session','package_tools'}
                   or not isinstance(v, str) or len(v) > 120
                   for k,v in osdata.items()):
                return
            from .diagnostics.package_sources131 import valid_summary
            if not valid_summary(raw.get('packages', {})):
                return
            raw.setdefault('packages', {})  # Compatible with older v119-v130 profiles.
            self.data = raw
        except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
            pass

    @property
    def complete(self) -> bool:
        return bool(self.data.get('complete')) and LOCAL_IDS.issubset(self.data['checks'])

    def due_areas(self, *, now=None, new_signatures=None) -> tuple[str, ...]:
        current = float(self.clock() if now is None else now)
        stamps = new_signatures if new_signatures is not None else self.signature_source()
        result = []
        for area in WATCH_PATHS:
            last = float(self.data['area_updated'].get(area, 0) or 0)
            changed = self.data['signatures'].get(area) != stamps.get(area)
            missing = any(f'{a}/{c}' not in self.data['checks'] for a, c in LOCAL_PLAN if a == area)
            if (changed or missing or (area == 'applications' and not self.data.get('packages'))
                    or current < last or current - last > AREA_TTLS[area]):
                result.append(area)
        return tuple(result)

    def pending_checks(self) -> tuple[tuple[str, str], ...]:
        due = set(self.due_areas())
        return tuple((a, c) for a, c in LOCAL_PLAN if a in due)

    def update(self, results, *, scanned_areas=None, new_signatures=None, browser=None, osinfo=None, packages=None):
        """Commit only completed measurements, without raw evidence/logs."""
        valid: dict[str, dict] = {}
        for item in results:
            if not isinstance(item, DiagnosticResult):
                continue
            key = f'{item.category_key}/{item.check_key}'
            if key in LOCAL_IDS:
                valid[key] = {
                    'status': item.status.value,
                    'summary': _safe_summary(key, item.diagnosis),
                }
        if not valid and browser is None and osinfo is None and packages is None:
            return
        self.data['checks'].update(valid)
        now = float(self.clock())
        # Only mark a full area fresh if every check in that area was measured.
        covered = set(valid)
        groups = tuple(scanned_areas or ())
        if new_signatures is None:
            new_signatures = self.signature_source()
        for area in groups:
            expected = {f'{a}/{c}' for a, c in LOCAL_PLAN if a == area}
            if expected.issubset(covered):
                self.data['area_updated'][area] = now
                self.data['signatures'][area] = new_signatures.get(area, '')
        if packages is not None:
            from .diagnostics.package_sources131 import valid_summary
            if valid_summary(packages):
                self.data['packages'] = packages
        if osinfo is not None:
            self.data['os'] = {k: v for k, v in osinfo.items()
                               if k in {'distro_id','distro_name','distro_version','kernel',
                                        'desktop','session','package_tools'}
                               and isinstance(v, str) and len(v) <= 120}
        if browser is not None:
            self.data['browser'] = {str(k): str(v) for k, v in browser.items()
                                    if k in {'browser_default','browser_handlers','browser_launcher',
                                             'browser_flatpak_apps', 'browser_package_sources', 'default_html', 'default_pdf',
                                             'default_images', 'default_text',
                                             'installed_flatpak_count', 'installed_flatpaks'}
                                    and isinstance(v, str) and len(v) <= (32000 if k == 'installed_flatpaks' else 160)}
        self.data['complete'] = LOCAL_IDS.issubset(self.data['checks'])
        self.data['updated_at'] = datetime.fromtimestamp(now, tz=timezone.utc).isoformat()
        self._save()

    def note(self, subject: str) -> str:
        """A small, labelled starting point, never a current diagnosis."""
        if not self.data['checks']:
            return ''
        low = subject.lower()
        parts = []
        stale = set(self.due_areas())
        if 'system' not in stale:
            distro = self.data.get('os', {}).get('distro_name', '')
            de = self.data.get('os', {}).get('desktop', '')
            if distro: parts.append('Linux: ' + distro)
            if de: parts.append('Desktop: ' + de)
        if 'applications' not in stale and any(x in low for x in ('browser', 'firefox', 'chrome', 'website', 'internet', 'web page')):
            name = self.data['browser'].get('browser_default', '')
            if name and name not in ('unknown', 'unrecognised'):
                parts.append('Default browser: ' + name.replace('_', ' '))
            flatpaks = self.data['browser'].get('browser_flatpak_apps', '')
            if flatpaks and flatpaks not in ('unknown', 'none_found'):
                parts.append('Detected Flatpak browsers: ' + flatpaks.replace('_', ' ').replace('|', ', '))
        if 'graphics' not in stale and any(x in low for x in ('gpu', 'graphics', 'display', 'screen')):
            summary = self.data['checks'].get('graphics/gpu', {}).get('summary', '')
            if summary: parts.append('Graphics: ' + summary)
        if 'audio' not in stale and any(x in low for x in ('bluetooth', 'headset', 'speaker')):
            status = self.data['checks'].get('audio/bluetooth', {}).get('status', '')
            if status: parts.append('Last Bluetooth inventory status: ' + status)
        if 'applications' not in stale and any(x in low for x in ('pdf', 'image', 'picture', 'photo', 'text file')):
            kind = 'pdf' if 'pdf' in low else 'images' if any(x in low for x in ('image','picture','photo')) else 'text'
            handler = self.data['browser'].get('default_' + kind, '')
            if handler:
                parts.append('Default ' + kind + ' application: ' + handler.replace('_', ' '))
        if not parts:
            return ''
        return ('**Saved system profile (starting information, not a new test):** '
                + '; '.join(parts[:3]) + '. I will check current symptoms separately.')

    def _save(self):
        tmp = None
        try:
            directory = self.path.parent
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            if directory.is_symlink():
                return
            os.chmod(directory, 0o700)
            if self.path.is_symlink():
                return
            fd, name = tempfile.mkstemp(prefix='.profile-', dir=directory)
            tmp = Path(name)
            with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                os.fchmod(stream.fileno(), 0o600)
                json.dump(self.data, stream, ensure_ascii=True, separators=(',', ':'), sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self.path)
        except OSError:
            # Diagnostic continues in memory if the state partition is full.
            pass
        finally:
            if tmp is not None:
                try: tmp.unlink(missing_ok=True)
                except OSError: pass

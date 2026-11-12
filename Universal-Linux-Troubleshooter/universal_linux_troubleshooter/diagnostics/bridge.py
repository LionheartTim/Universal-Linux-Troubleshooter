"""Read-only Linux host diagnostic bridge.

Every command uses a strictly limited argv (never a shell), timeout and bounded
output. No command needs privilege or changes the host. Network access is only
possible from the opt-in external TLS check after an explicit UI question.
Tests can inject a host adapter to exercise every result without touching Linux.
An UNKNOWN result means insufficient evidence, NOT a healthy machine.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import socket
import ssl
import subprocess
from typing import Callable

from ..results import DiagnosticResult, ResultStatus
from ..flatpak_host138 import in_flatpak, view_path, host_read, host_disk_usage, host_path_exists
from .guidance import guided_solution
from .journal_analysis import analyze_journal_json

GiB = 1024 ** 3
MiB = 1024 ** 2


@dataclass(frozen=True)
class CommandOutput:
    code: int
    out: str
    err: str = ""
    truncated: bool = False  # Was output cut to the safe size limit?


class LocalHost:
    """Limited, inspectable host-I/O surface. No writes, sudo or shell calls."""

    def list_names(self, directory: str) -> tuple[str, ...]:
        return tuple(sorted(os.listdir(view_path(directory))))

    def exists(self, path: str) -> bool:
        if in_flatpak() and path in ('/sysroot','/run/ostree-booted'):
            return host_path_exists(path)
        return view_path(path).exists()

    def read(self, path: str) -> str:
        if in_flatpak() and path in ('/proc/mounts','/proc/self/mounts','/proc/meminfo'):
            return host_read(path)
        return view_path(path).read_text(encoding="utf-8", errors="replace")[:16384]

    def disk_usage(self, path: str):
        return host_disk_usage(path) if in_flatpak() else shutil.disk_usage(path)

    def load_average(self) -> tuple[float, float, float]:
        return os.getloadavg()

    def cpu_count(self) -> int:
        return os.cpu_count() or 1

    def external_tls_probe(self) -> tuple[bool, str]:
        """One direct, bounded TLS handshake, no HTTP request and no log upload.

        NEVER call except via DiagnosticBridge(allow_network=True) after UI consent.
        """
        server = "www.mozilla.org"
        try:
            with socket.create_connection((server, 443), timeout=4) as sock:
                with ssl.create_default_context().wrap_socket(sock, server_hostname=server) as tls:
                    tls.settimeout(4)
                    return True, "Secure connection established."
        except (OSError, ssl.SSLError, TimeoutError) as exc:
            return False, f"Connection failed: {type(exc).__name__}."

    def command(self, argv: tuple[str, ...]) -> CommandOutput:
        # Explicitly fixed argv, no shell interpolation, no network or mutations.
        permitted = {
            ("ip", "-j", "address", "show"),
            ("systemd-analyze", "time"),
            ("flatpak", "list", "--app", "--user", "--columns=application"),
            ("flatpak", "list", "--app", "--system", "--columns=application"),
            ("journalctl", "-b", "-u", "NetworkManager", "-n", "80", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-k", "-n", "120", "--no-pager", "--output=json"),
            ("journalctl", "--user", "-b", "-n", "100", "--no-pager", "--output=json"),
            ("ip", "-j", "route", "show", "default"),
            ("ip", "-j", "-6", "route", "show", "default"),
            ("lsblk", "-J", "-b", "-o", "NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO"),
            ("systemctl", "--failed", "--no-pager", "--no-legend", "--plain"),
            ("journalctl", "-b", "-p", "0..3", "-n", "80", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-p", "0..3", "-n", "20", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-p", "0..3", "-n", "8", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-p", "0..4", "-n", "8", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-p", "0..4", "-n", "160", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-n", "160", "--no-pager", "--output=json"),
            ("journalctl", "-b", "-p", "0..4", "-n", "40", "--no-pager", "--output=json"),
            ("nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"),
            ("lspci", "-nn"),
            ("flatpak", "list", "--app", "--user", "--columns=application,origin"),
            ("flatpak", "list", "--app", "--system", "--columns=application,origin"),
            ("pactl", "--format=json", "list", "sources"),
            ("pactl", "--format=json", "list", "sinks"),
            ("pactl", "get-default-source"),
            ("pactl", "get-default-sink"),
            ("xdg-mime", "query", "default", "application/pdf"),
            ("xdg-mime", "query", "default", "image/png"),
            ("xdg-mime", "query", "default", "text/html"),
            ("xdg-mime", "query", "default", "text/plain"),
            ("pacman", "-Qdtq"),
            ("pacman", "-Qq"),
            ("podman", "ps", "-a", "--format", "json"),
            ("podman", "info", "--format", "json"),
            ("virsh", "list", "--all", "--name"),
            ("fc-list", "--format=%{family}\\n"),
            ("ss", "-H", "-ltnu"),
            ("ip", "-j", "link", "show"),
            ("systemctl", "is-active", "bluetooth.service"),
            ("systemctl", "is-active", "libvirtd.service"),
            ("systemctl", "is-active", "virtqemud.service"),
            ("systemctl", "--user", "is-active", "pipewire.service"),
            ("systemctl", "--user", "is-active", "wireplumber.service"),
            ("systemctl", "--user", "is-active", "pulseaudio.service"),
            ("rpm-ostree", "status", "--json"),
            ("xdg-settings", "get", "default-web-browser"),
            ("xdg-mime", "query", "default", "x-scheme-handler/https"),
            ("timedatectl", "show", "-p", "NTPSynchronized", "--value"),
            ("getent", "ahostsv4", "www.mozilla.org"),
            ("coredumpctl", "--no-legend", "--no-pager", "-n", "30", "list"),
        }
        from .package_sources131 import SOURCES
        permitted.update(SOURCES.values())
        # SMART health reads are permitted only for known block-device names.
        smart = (len(argv) == 7 and argv[:6] ==
                 ("smartctl", "-j", "-H", "-A", "-n", "standby") and
                 re.fullmatch(r"/dev/(?:sd[a-z]{1,3}|hd[a-z]{1,3}|vd[a-z]{1,3}|xvd[a-z]{1,3}|nvme\d{1,3}n\d{1,3}|mmcblk\d{1,3})", argv[6]))
        if argv not in permitted and not smart:
            raise ValueError("Command not approved as a read-only diagnostic")
        try:
            # The Flatpak runtime is NOT the host distribution. Send only
            # already-allowlisted argv to the host, never a shell command.
            actual_argv = (
                ('flatpak-spawn','--host','--env=LC_ALL=C','--env=LANG=C', *argv)
                if in_flatpak() else argv
            )
            result = subprocess.run(
                actual_argv, capture_output=True, text=True, errors="replace", timeout=8,
                check=False, env={**os.environ, "LC_ALL": "C", "LANG": "C"},
            )
        except FileNotFoundError:
            return CommandOutput(127, "", f"Required utility unavailable: {argv[0]}")
        except subprocess.TimeoutExpired:
            return CommandOutput(124, "", f"Read-only utility timed out: {argv[0]}")
        except OSError as exc:
            return CommandOutput(125, "", f"Cannot execute {argv[0]}: {type(exc).__name__}")
        return CommandOutput(result.returncode, result.stdout[:131072], result.stderr[:2048],
                             truncated=len(result.stdout) > 131072)


def _result(category: str, check: str, status: ResultStatus, summary: str,
            explanation: str, next_steps: str, evidence: list[str] | tuple[str, ...],
            *, specific_guidance: bool = False) -> DiagnosticResult:
    # Limit displayed evidence in case a utility reports unexpected volumes.
    # The system journal can contain up to 80 different areas. Preserve all
    # grouped areas in Evidence / Logs; the query itself already bounds the
    # number of events. Other checks keep the smaller general evidence limit.
    max_evidence = 250 if (category, check) == ("system", "system_logs") else 36
    return DiagnosticResult(category, check, status, summary, explanation,
                            (next_steps if specific_guidance else guided_solution(category, check, status, next_steps)),
                            tuple(s[:800] for s in evidence[:max_evidence]))


def _unknown(category: str, check: str, why: str, source: str = "") -> DiagnosticResult:
    return _result(
        category, check, ResultStatus.UNKNOWN, "Could not complete this check",
        why + " This does not tell us whether your computer has a problem.",
        "Read the details in Evidence / Logs. Then try this check again. "
        "Nothing on your computer has been changed.",
        (["Source: " + source] if source else []) + ["Limit: " + why],
    )


def _safe_interface(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.:@-]{1,64}", name))


def check_adapters(host: LocalHost) -> DiagnosticResult:
    try:
        names = [n for n in host.list_names("/sys/class/net") if _safe_interface(n) and n != "lo"]
    except OSError as exc:
        return _unknown("network", "adapter", f"Cannot read network interfaces ({type(exc).__name__}).", "/sys/class/net")
    observations = []
    operating_states = []
    for name in names[:32]:
        try:
            state = host.read(f"/sys/class/net/{name}/operstate").strip()
        except OSError:
            state = "unknown"
        operating_states.append(state.lower() or "unknown")
        observations.append(f"{name}: operating state {state or 'unknown'}")
    if not names:
        return _result("network", "adapter", ResultStatus.WARNING,
                       "Linux could not find a normal network connection",
                       "Linux did not find a network device it could use for Wi-Fi or a network cable. "
                       "This does not prove that the device is broken.",
                       "Check whether the adapter appears in your firmware or system hardware tools. "
                       "If using a VM or container, verify that a network interface is configured.",
                       ["Source: /sys/class/net", "Only loopback, or no entries visible"])
    up_count = sum(state == "up" for state in operating_states)
    down_count = sum(state == "down" for state in operating_states)
    return _result("network", "adapter", ResultStatus.OK,
                   f"Linux found {len(names)} network connection(s): {up_count} active, {down_count} inactive",
                   "Linux gave us a list of connections and whether they are on or off. "
                   f"This check examined {len(operating_states)} connections: {up_count} active and {down_count} inactive. "
                   "An unused connection can be off without anything being wrong. "
                   "This is a device list, not a test of internet access.",
                   "If connectivity is failing, run IP configuration next. A 'down' interface "
                   "can be intentionally inactive; confirm it should be connected before changing anything.",
                   ["Source: /sys/class/net"] + observations)


def check_ip(host: LocalHost) -> DiagnosticResult:
    cmd = host.command(("ip", "-j", "address", "show"))
    if cmd.code != 0:
        return _unknown("network", "ip", f"Cannot read IP address configuration: {cmd.err or 'ip exited with an error' }", "ip -j address show")
    try:
        addresses = json.loads(cmd.out)
        if not isinstance(addresses, list):
            raise ValueError("Unexpected JSON root")
    except (ValueError, TypeError):
        return _unknown("network", "ip", "The ip utility returned data that could not be interpreted.", "ip -j address show")
    interfaces = []
    nonloop = 0
    for item in addresses:
        if not isinstance(item, dict):
            continue
        name = str(item.get("ifname", "unknown"))[:64]
        if name == "lo":
            continue
        infos = item.get("addr_info") or []
        ip_list = [str(i.get("local", "")) for i in infos if isinstance(i, dict) and i.get("family") in ("inet", "inet6") and i.get("local")]
        if ip_list:
            nonloop += 1
        interfaces.append(f"{name}: {', '.join(ip_list[:5]) or 'no IPv4/IPv6 address'}")
    ipv4 = host.command(("ip", "-j", "route", "show", "default"))
    ipv6 = host.command(("ip", "-j", "-6", "route", "show", "default"))
    routes: list[str] = []
    have_route = False
    for label, response in (("IPv4", ipv4), ("IPv6", ipv6)):
        if response.code == 0:
            try:
                r = json.loads(response.out)
                if not isinstance(r, list):
                    raise ValueError("Invalid routes")
                for entry in r[:4]:
                    if isinstance(entry, dict):
                        have_route = True
                        routes.append(f"{label} default: via {entry.get('gateway', '(on-link)')} dev {entry.get('dev', '?')}")
            except (ValueError, TypeError):
                routes.append(f"{label} route data could not be interpreted")
        else:
            routes.append(f"{label} route check unavailable ({response.err or 'command failed'})")
    evidence = ["Sources: ip -j address show; ip -j route show default; ip -j -6 route show default"] + interfaces[:20] + routes
    if not interfaces:
        return _result("network", "ip", ResultStatus.WARNING,
                       "No usable network connection was found in the settings",
                       "Linux only showed an internal connection that the computer uses to talk to itself.",
                       "Start with Network adapters, and check whether the device is enabled and connected.", evidence)
    if not nonloop:
        return _result("network", "ip", ResultStatus.WARNING,
                       "No network address was found for the connections",
                       "The listed connections do not have an IP address (an address used to talk to other devices). "
                       "This can be normal if you are not using those connections.",
                       "Confirm which interface should be connected. Review its network-manager "
                       "connection settings and DHCP status manually.", evidence)
    if not have_route:
        # No routes / unavailable tools are not conclusive; avoid claiming a bad gateway.
        return _result("network", "ip", ResultStatus.UNKNOWN,
                       "Your computer has a network address, but the path to the internet is unclear",
                       "At least one connection has an IP address, but this check could not confirm a route to the internet. "
                       "This can be normal on a network that is not supposed to have internet access.",
                       "Inspect the intended connection and gateway settings. If internet access is "
                       "needed, check which interface should provide the default route.", evidence)
    return _result("network", "ip", ResultStatus.OK,
                   "Your computer has a network address and a route out of the network",
                   "Your computer has an address on the network and knows where to send traffic. "
                   "This check did not test whether websites or the internet are reachable.",
                   "If websites still fail, use Website name check (with your permission) and Local gateway "
                   "in Internet & Network. Local gateway only reads saved router settings. "
                   "Website name check may contact your normal DNS server, but does not open a web page.", evidence)


def _composefs_root(host: LocalHost) -> bool:
    """Identify a composefs root using mount metadata (not a guessed small size).

    Atomic systems may report an overlay/EROFS-backed composefs image as `/`.
    A regular overlay container is *not* automatically a composefs host.
    """
    for path in ("/proc/self/mountinfo", "/proc/mounts"):
        try:
            content = host.read(path)
        except (OSError, KeyError, ValueError):
            continue
        if path.endswith("mountinfo"):
            for line in content.splitlines():
                before, sep, after = line.partition(" - ")
                parts = before.split()
                props = after.split()
                if sep and len(parts) > 4 and parts[4] == "/" and len(props) >= 2:
                    fstype, source = props[:2]
                    if "composefs" in source.lower() or fstype == "composefs":
                        return True
                    if fstype == "erofs" and host.exists("/run/ostree-booted"):
                        return True
                    # Do not treat arbitrary overlay/container roots as composefs.
                    return False
        else:
            for line in content.splitlines():
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "/":
                    return "composefs" in parts[0].lower() or parts[2] == "composefs" or (parts[2] == "erofs" and host.exists("/run/ostree-booted"))
    return False


def _format_usage(path: str, usage) -> str:
    fraction = 100 * usage.free / usage.total if usage.total > 0 else 0
    return f"{path}: {usage.free / GiB:.2f} GiB free of {usage.total / GiB:.2f} GiB ({fraction:.1f}% free)"


def _low_capacity(usage) -> bool:
    return usage.free < 2 * GiB and usage.free / usage.total < 0.10


def check_space(host: LocalHost) -> DiagnosticResult:
    if _composefs_root(host):
        evidence = [
            "Root / uses composefs: its full, read-only image is expected and is NOT a disk-full warning.",
            "Source: /proc/self/mountinfo or /proc/mounts; writable storage via statvfs.",
        ]
        # On Fedora Atomic the user-data location is /var; /sysroot is its backing root.
        # If /var is unavailable, do NOT turn the full composefs image into a warning.
        try:
            writable = host.disk_usage("/var")
            if writable.total <= 0:
                raise ValueError("Invalid filesystem capacity")
        except (OSError, ValueError) as exc:
            return _unknown("storage", "space", f"composefs root detected, but real writable /var storage cannot be measured ({type(exc).__name__}).", "/var")
        evidence.append(_format_usage("/var (persistent writable data)", writable))
        # Display underlying capacity for context when accessible, but do not count
        # the same disk twice or treat /sysroot being read-only as an error.
        backing = None
        try:
            if host.exists("/sysroot"):
                backing = host.disk_usage("/sysroot")
                if backing.total > 0:
                    evidence.append(_format_usage("/sysroot (backing filesystem)", backing))
        except (OSError, ValueError):
            evidence.append("/sysroot backing capacity unavailable (not required for /var check)")
        low_var = _low_capacity(writable)
        low_backing = backing is not None and backing.total > 0 and _low_capacity(backing)
        if low_var or low_backing:
            affected = "/var" if low_var else "/sysroot"
            return _result(
                "storage", "space", ResultStatus.WARNING,
                f"There may be little free space for your files in {affected} (the composefs system area is normally full)",
                "On Bazzite and similar Linux versions, the system area called composefs can look full. That is normal. "
                f"But the separate area {affected}, where files can be saved, has less than 2 GiB "
                "and less than 10% of its space free. Check this before removing anything.",
                "Inspect df -h /var /sysroot. Review only your own stored data and "
                "follow the distribution's supported cleanup method. Do not delete deployments manually. "
                "No changes are made by this program.",
                evidence, specific_guidance=True,
            )
        return _result(
            "storage", "space", ResultStatus.OK,
            "Your file storage has enough space; the full composefs system area is normal",
            "On Bazzite and some other Linux versions, the protected system area (composefs) can show 100% full. "
            "That is normal. The separate area that stores your files (/var) has enough space for this check. "
            "Other disks and special storage limits have not been checked.",
            "No cleanup is needed based on this check. To see the measured free space, "
            "open 'Evidence / Logs'. No files were changed.",
            evidence, specific_guidance=True,
        )
    try:
        usage = host.disk_usage("/")
    except OSError as exc:
        return _unknown("storage", "space", f"Cannot read root filesystem usage ({type(exc).__name__}).", "statvfs(/)")
    if usage.total <= 0:
        return _unknown("storage", "space", "Root filesystem returned zero total capacity.", "statvfs(/)")
    evidence = ["Source: statvfs(/), via Python shutil.disk_usage", _format_usage("/", usage)]
    if _low_capacity(usage):
        return _result("storage", "space", ResultStatus.WARNING,
                       "Your main disk may be nearly full",
                       "Your main file storage has less than 2 GiB and less than 10% free. "
                       "Some small or special disks can work normally with this amount.",
                       "Inspect disk usage and remove only files you recognize. On atomic Linux "
                       "systems, follow the distro's supported cleanup procedure; do not delete deployment files manually. "
                       "Re-run this check after your changes.", evidence)
    return _result("storage", "space", ResultStatus.OK,
                   "Your main file storage has enough free space",
                   "The main place where Linux stores files has enough space for now. "
                   "Other disks may still be full, and this does not check whether any disk is damaged.",
                   "If an application reports that its disk is full, check its specific mount "
                   "or user data directory; those may be on a different filesystem.", evidence)


def check_drives(host: LocalHost) -> DiagnosticResult:
    out = host.command(("lsblk", "-J", "-b", "-o", "NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO"))
    if out.code != 0:
        return _unknown("storage", "drives", f"Cannot read device inventory: {out.err or 'lsblk failed' }", "lsblk (read-only)")
    try:
        obj = json.loads(out.out)
        devices = obj["blockdevices"]
        if not isinstance(devices, list):
            raise ValueError("Invalid blockdevices")
    except (KeyError, TypeError, ValueError):
        return _unknown("storage", "drives", "The device inventory output was not interpretable.", "lsblk JSON")
    observed = []
    def visit(items, depth=0):
        for entry in items:
            if not isinstance(entry, dict) or len(observed) >= 30:
                continue
            name = str(entry.get("name") or "unknown")[:64]
            kind = str(entry.get("type") or "?")[:32]
            size = entry.get("size") or 0
            value = round(size / GiB, 2) if isinstance(size, (int, float)) and size >= 0 else "unknown"
            mount = str(entry.get("mountpoint") or "not mounted")[:120]
            observed.append(f"{'  ' * min(depth, 5)}{name} ({kind}, {value} GiB), mount: {mount}")
            visit(entry.get("children") or [], depth + 1)
    visit(devices)
    if not observed:
        return _unknown("storage", "drives", "No block devices were reported (for example in a restricted container).", "lsblk JSON")
    return _result("storage", "drives", ResultStatus.OK, "Linux found your disks and storage devices",
                   "Linux listed the disks and their storage areas. This is only a list. "
                   "It is not a SMART health test and does not prove that a drive is healthy.",
                   "If you suspect a failing drive, save your important files and run "
                   "Drive health indicators. This check may need the smartmontools program and permission to read the disk.",
                   ["Source: lsblk -J -b -o NAME,TYPE,SIZE,MOUNTPOINT,MODEL,RO"] + observed)


def check_resources(host: LocalHost) -> DiagnosticResult:
    try:
        content = host.read("/proc/meminfo")
        pairs = dict((k.strip(), int(v.strip().split()[0])) for k, v in
                     (line.split(":", 1) for line in content.splitlines() if ":" in line))
        total, avail = pairs["MemTotal"], pairs["MemAvailable"]
        if total <= 0:
            raise ValueError("Invalid total memory")
    except (OSError, ValueError, KeyError, IndexError):
        return _unknown("applications", "resources", "Memory availability could not be read from /proc/meminfo.", "/proc/meminfo")
    lines = ["Source: /proc/meminfo", f"Memory available: {avail / 1024:.0f} MiB of {total / 1024:.0f} MiB"]
    try:
        one, five, fifteen = host.load_average()
        lines.append(f"System load average (1/5/15 min): {one:.2f} / {five:.2f} / {fifteen:.2f}; logical CPUs: {host.cpu_count()}")
    except (OSError, ValueError):
        lines.append("Load average unavailable")
    if avail < 512 * 1024 and avail / total < 0.05:
        return _result("applications", "resources", ResultStatus.WARNING,
                       "Your computer has very little free working memory right now",
                       "At the time of the check, your computer had less than 512 MiB (about half a gigabyte) "
                       "and less than 5% of its working memory (RAM) free. "
                       "This check cannot tell which app is using that memory.",
                       "Review memory use in a system monitor and reproduce the issue while watching it. "
                       "Save work before closing memory-heavy applications yourself.", lines)
    return _result("applications", "resources", ResultStatus.OK,
                   "Your computer has enough free working memory right now",
                   "Enough working memory (RAM) was available during this check. "
                   "Memory can run low at other times, so this does not rule out occasional problems.",
                   "If freezes are intermittent, collect readings when the problem occurs. "
                   "Avoid assuming that a quiet snapshot proves there is no issue.", lines)


def check_services(host: LocalHost) -> DiagnosticResult:
    out = host.command(("systemctl", "--failed", "--no-pager", "--no-legend", "--plain"))
    if out.code != 0:
        return _unknown("applications", "services", f"Service status unavailable: {out.err or 'systemctl failed' }", "systemctl --failed")
    failures = [line.strip() for line in out.out.splitlines() if line.strip()]
    if failures:
        return _result("applications", "services", ResultStatus.WARNING,
                       f"Linux reports {len(failures)} background program(s) that failed",
                       "One or more programs that run in the background did not work as expected. "
                       "This may have nothing to do with the problem you noticed.",
                       "Identify which failed unit relates to your symptoms. Review its logs "
                       "and follow the relevant distro documentation before restarting or changing anything.",
                       ["Source: systemctl --failed --no-pager --no-legend --plain"] + failures[:25])
    return _result("applications", "services", ResultStatus.OK,
                   "Linux did not report failed system services in this check",
                   "The available list contains no failed background system services. "
                   "This check does not examine every program on the computer.",
                   "For a specific application problem, inspect its user-session services "
                   "and app logs when their dedicated checks become available.",
                   ["Source: systemctl --failed --no-pager --no-legend --plain", "No failed units in command output"])


def check_system_logs(host: LocalHost) -> DiagnosticResult:
    commands = tuple(("journalctl", "-b", "-p", "0..3", "-n", str(n), "--no-pager", "--output=json")
                     for n in (80, 20, 8))
    attempts = []
    for number, command in zip((80, 20, 8), commands):
        out = host.command(command)
        stderr = out.err.strip()[:240]
        if any(v in stderr.casefold() for v in ("permission denied", "access denied", "not seeing messages", "insufficient permissions", "no journal files were opened")):
            return _unknown("system", "system_logs", "Linux did not allow your account to read these system messages: " + stderr, "journalctl")
        if out.code == 127:
            return _unknown("system", "system_logs", "journalctl is not available.", "journalctl")
        if out.code != 0:
            attempts.append(f"A reading of {number} messages failed (code {out.code}): {stderr}")
            if out.code in (125, 126):
                break
            continue
        if out.truncated:
            attempts.append(f"The {number}-message sample exceeded the output limit.")
            continue
        if not out.out.strip() or out.out.strip() == "-- No entries --":
            return _result("system", "system_logs", ResultStatus.INFO,
                           "No high-priority system messages were visible",
                           "Linux returned no urgent messages for the current startup in the available journal. "
                           "Some protected or older messages might not be included; no hardware health test was performed.",
                           "No action is needed based on this list. If a problem continues, try the check closest to that problem.",
                           ["Source: current-boot journal, priorities 0–3", f"Requested up to {number} recent messages.",
                            "No visible entries in the returned sample."] + attempts, specific_guidance=True)
        try:
            report = analyze_journal_json(out.out)
        except ValueError:
            attempts.append(f"The {number}-message sample contained unreadable records.")
            continue
        # Follow up relevant *recognized* messages automatically with existing
        # allowlisted local checks. No network, privilege request or repair.
        mapping = {
            "Bluetooth": ("audio", "bluetooth", "Bluetooth status"),
            "Network": ("network", "ip", "IP configuration"),
            "Storage / filesystem": ("storage", "space", "Disk space"),
            "Graphics": ("graphics", "gpu", "GPU inventory"),
        }
        followups = []
        used = set()
        # Only recognized errors normally justify automatic followup. A
        # graphics-grouped urgent message also gets targeted *read-only*
        # checks because a generic journal group alone is not diagnostic.
        for area in dict.fromkeys((*report.recognized_areas,
                                   *(x for x in report.observed_areas if x == "Graphics"))):
            targets = (("graphics", "render", "Graphics errors"),
                       ("graphics", "gpu", "GPU inventory"),
                       ("graphics", "display", "Display configuration")) if area == "Graphics" else (mapping.get(area),)
            if area.startswith(("Service: ", "Unit: ")):
                targets = (("applications", "services", "Service status"),)
            for target in targets:
                if not target or (target[0], target[1]) in used or len(followups) >= 5:
                    continue
                used.add((target[0], target[1]))
                try:
                    observed = READY_CHECKS[(target[0], target[1])](host)
                    followups.append((target[2], observed))
                except Exception:
                    # A secondary reader failing must not lose the primary journal.
                    continue
        followup_report = ("\n\nRelated local checks performed automatically:\n" +
                           "\n".join(f"- {label}: {item.status.value} — {item.diagnosis}"
                                      for label, item in followups)) if followups else ""
        extra_proof = (["Automatic related read-only check: " + label +
                        " | status: " + item.status.value + " | " + item.diagnosis
                        for label, item in followups])
        route_evaluation = ""
        graphics_check = next((r for label,r in followups if label == "Graphics errors"), None)
        if graphics_check is not None:
            graphics_text = (graphics_check.diagnosis + " " + " ".join(graphics_check.evidence)).casefold()
            explicit_failure = any(word in graphics_text for word in
                                   ("gpu reset", "gpu hang", "ring timeout", "gpu fault", "nvrm: xid"))
            if (graphics_check.status in (ResultStatus.WARNING, ResultStatus.PROBLEM)
                    and explicit_failure):
                route_evaluation = (
                    "\n\nAutomatic graphics followup — a driver reset/hang was recorded.\n"
                    "1. Save your work and open your distribution's usual system update screen.\n"
                    "2. Apply supported updates yourself; on Atomic Linux, use the supported system updater rather than overwriting drivers.\n"
                    "3. Repeat the task once and check whether a NEW graphics error appears.\n"
                    "4. If it persists, the app-specific and display-connection alternatives remain available."
                )
            else:
                route_evaluation = (
                    "\n\nAutomatic graphics followup — no specific GPU reset was confirmed by the extra check.\n"
                    "1. If only one optional app freezes, try its supported update or close that app and retest the affected workflow.\n"
                    "2. If only a monitor loses its signal, check its power, selected input and accessible cable.\n"
                    "3. If different programs still fail, check for supported distribution updates; do not manually replace drivers.\n"
                    "4. If the problem persists, provide the graphics device name, time and redacted message to the affected developer or device support."
                )
        if followups:
            followup_report += ("\nA related measurement can support a finding, "
                                "but does not establish that two events have the same cause.")
            # Give the user the actual measured outcome in the proposed route;
            # do not merely instruct them to run another check.
            if any(label == "Graphics errors" for label, _ in followups):
                observed = next(r for label, r in followups if label == "Graphics errors")
                interpretation = ("The graphics-error check recorded its own warning; compare its exact message "
                                  "and time with the affected application."
                                  if observed.status in (ResultStatus.WARNING, ResultStatus.PROBLEM)
                                  else "The separate graphics-error check did not establish a specific driver failure. "
                                       "Application-only, monitor-path and system-update routes remain alternatives.")
                followup_report += "\nGraphics followup interpretation: " + interpretation
        return _result("system", "system_logs", ResultStatus.WARNING,
                       report.diagnosis, report.explanation + followup_report, report.solution + route_evaluation,
                       list(report.evidence) + extra_proof + attempts +
                       ([f"Limited sample: only up to {number} recent messages were readable."] if number < 80 else []),
                       specific_guidance=True)
    return _unknown("system", "system_logs",
                    "The system journal could not be read completely. " + " ".join(attempts),
                    "journalctl current boot")


READY_CHECKS: dict[tuple[str, str], Callable[[LocalHost], DiagnosticResult]] = {
    ("network", "adapter"): check_adapters,
    ("network", "ip"): check_ip,
    ("storage", "space"): check_space,
    ("storage", "drives"): check_drives,
    ("applications", "resources"): check_resources,
    ("applications", "services"): check_services,
    ("system", "system_logs"): check_system_logs,
}


# Additional offline readers use the same whitelisted host access and output contract.
from .additional_checks import ADDITIONAL_READY_CHECKS
from .remaining_checks import check_drive_health, check_external
READY_CHECKS.update(ADDITIONAL_READY_CHECKS)
READY_CHECKS[("storage", "health")] = check_drive_health
READY_CHECKS[("network", "external")] = check_external


class DiagnosticBridge:
    def __init__(self, host: LocalHost | None = None, *, allow_network: bool = False):
        self.host = host if host is not None else LocalHost()
        self.allow_network = bool(allow_network)

    def run_check(self, category: str, check: str) -> DiagnosticResult:
        handler = READY_CHECKS.get((category, check))
        if handler is None:
            raise ValueError("Diagnostic check is not yet implemented")
        try:
            if (category, check) == ("network", "external"):
                return check_external(self.host, allow_network=self.allow_network)
            if (category, check) == ("network", "dns"):
                from .additional_checks import check_dns
                return check_dns(self.host, allow_network=self.allow_network)
            return handler(self.host)
        except Exception as exc:
            # A fault in one diagnostic must not trigger repairs or crash the UI.
            return _unknown(category, check, f"Diagnostic failed safely ({type(exc).__name__}).")

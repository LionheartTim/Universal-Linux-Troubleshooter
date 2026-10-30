"""Flatpak host-data adapter for read-only Manual Diagnostics.

Only the already approved diagnostic argv may be sent through flatpak-spawn.
No shell, sudo, writes, app launch or unattended repair is offered here.
Failure remains UNKNOWN in existing diagnostic code (not a normal result).
"""
from __future__ import annotations
import os
from pathlib import Path
import re
import subprocess


def in_flatpak() -> bool:
    return bool(os.environ.get('FLATPAK_ID'))


def view_path(path: str | Path) -> Path:
    """Map host configuration and OS data to Flatpak's read-only host mounts."""
    p = Path(path).expanduser()
    if not in_flatpak() or not p.is_absolute():
        return p
    raw = str(p)
    if raw == '/etc' or raw.startswith('/etc/'):
        return Path('/run/host/etc' + raw[4:])
    if raw == '/usr' or raw.startswith('/usr/'):
        return Path('/run/host/usr' + raw[4:])
    return p


def host_read(path: str, limit: int = 16384) -> str:
    """Read limited public kernel metadata from the host, not sandbox /proc.

    No arbitrary file path or user private file is accepted for spawn.
    """
    if path not in ('/proc/mounts', '/proc/self/mounts', '/proc/meminfo'):
        raise ValueError('Not an approved host metadata file')
    args = ('flatpak-spawn', '--host', '--env=LC_ALL=C', 'cat', path)
    out = subprocess.run(args, text=True, capture_output=True,
                         errors='replace', timeout=6, check=False)
    if out.returncode != 0:
        raise OSError('Host metadata unavailable')
    return out.stdout[:limit]


def host_disk_usage(path: str):
    """Return filesystem usage from the host, never from the sandbox root."""
    if path not in ('/', '/var', '/sysroot'):
        raise ValueError('Disk target not approved')
    from collections import namedtuple
    args = ('flatpak-spawn', '--host', '--env=LC_ALL=C',
            'df', '-B1', '--output=size,used,avail', path)
    out = subprocess.run(args, text=True, capture_output=True,
                         errors='replace', timeout=6, check=False)
    if out.returncode != 0:
        raise OSError('Host disk usage unavailable')
    rows = out.stdout.strip().splitlines()
    if len(rows) != 2:
        raise OSError('Unexpected host disk usage output')
    values = rows[1].split()
    if len(values) != 3 or not all(v.isdigit() for v in values):
        raise OSError('Invalid host disk usage output')
    disk = namedtuple('disk_usage', 'total used free')
    return disk(*(int(v) for v in values))


def host_path_exists(path: str) -> bool:
    if path not in ('/sysroot', '/run/ostree-booted'):
        raise ValueError('Host path not approved')
    out = subprocess.run(('flatpak-spawn','--host','test','-e',path),
                         capture_output=True, timeout=5, check=False)
    return out.returncode == 0

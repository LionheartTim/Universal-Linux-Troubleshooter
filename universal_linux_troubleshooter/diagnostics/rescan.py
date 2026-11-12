"""Small immutable replay descriptor for the last manually initiated scan.

It records the exact approved checks selected for a run, never captured
measurements. Re-running this descriptor starts new checks; it does not replay
or import results. Network permission is deliberately NOT stored as consent.
"""
from dataclasses import dataclass

OPTIONAL_NETWORK_CHECKS = frozenset({('network', 'dns'), ('network', 'external')})


@dataclass(frozen=True)
class ManualScanReplay:
    checks: tuple[tuple[str, str], ...]
    case_id: str | None = None
    topic_id: str | None = None
    focused_probes: tuple[str, ...] = ()
    complete: bool = False
    included_network: bool = False

    def is_available_for(self, *, case_id: str | None, topic_id: str | None) -> bool:
        """Do not rescan a different selected case under the old case name."""
        if self.case_id is None:
            return True  # Explicitly repeats the last check batch, not a new area.
        return self.case_id == case_id and self.topic_id == topic_id

    def checks_for_repeat(self, *, network_permitted: bool = False) -> tuple[tuple[str, str], ...]:
        """No internet requests survive from a previous scan without fresh consent."""
        if not network_permitted:
            return tuple(check for check in self.checks if check not in OPTIONAL_NETWORK_CHECKS)
        return self.checks

    @property
    def needs_network_permission(self) -> bool:
        return self.included_network and any(check in OPTIONAL_NETWORK_CHECKS for check in self.checks)

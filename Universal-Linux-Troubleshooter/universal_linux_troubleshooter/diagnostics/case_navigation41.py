"""AI-free, read-only navigation for the 250 documented diagnosis cases.

Navigation does not assess a fault, select a solution, or run shell commands.
Every catalog entry remains reachable both by browsing and by searching.
"""
from __future__ import annotations

from .manual_cases40 import browse_cases, case_catalog
from ..catalog import match_categories
from .topic_catalog127 import matching_topics

# Each documented category is in exactly one accessible subject under its
# original hardware/software domain. No new clinical/technical claim is made.
HARDWARE_SUBJECTS = (
    ("Graphics & Display", "graphics", ("graphics", "gpu", "display")),
    ("Audio & Bluetooth", "audio", ("audio",)),
    ("Hardware & Power", "hardware", ("hardware", "power", "board", "cpu", "memory", "cooling", "other")),
    ("Storage & Filesystems", "storage", ("storage",)),
    ("Peripherals & Devices", "hardware", ("peripherals", "camera", "printing")),
)
SOFTWARE_SUBJECTS = (
    ("Steam", "applications", ("gaming",)),
    ("Applications & Services", "applications", ("applications", "apps", "services")),
    ("Internet & Network", "network", ("network",)),
    ("System, Boot & Updates", "system", ("system", "boot", "packages")),
    ("Flatpak & AppImage", "applications", ("flatpak", "appimage")),
    ("Desktop & Display", "graphics", ("desktop", "display")),
    ("Audio & Devices", "audio", ("audio", "peripherals", "printing")),
    ("Virtual Machines & Containers", "virtualization", ("virtualization", "containers")),
    ("Security & Permissions", "applications", ("security",)),
    ("Development Tools", "applications", ("development",)),
    ("Storage & Filesystems", "storage", ("storage",)),
    ("Hardware Integration", "hardware", ("hardware",)),
)
SUBJECTS = {"hardware": HARDWARE_SUBJECTS, "software": SOFTWARE_SUBJECTS}


def navigation_groups(search: str = "") -> tuple[tuple[str, tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...]], ...]:
    """Return visible domain/subject/case triples, never silently losing cases.

    A matching subject name (or existing check title/description) exposes its
    members; otherwise only case titles/IDs/symptoms/aliases that match remain.
    """
    cases = case_catalog()
    lookup = {cid: (title, domain) for cid, title, domain in browse_cases(search=search)}
    q = search.strip().casefold()[:150]
    legacy_matches = {cat.key for cat in match_categories(search)} if q else set()
    result = []
    for domain in ("hardware", "software"):
        subjects = []
        domain_matches = q in domain if q else False
        for heading, category_key, original_categories in SUBJECTS[domain]:
            heading_matches = bool(q) and (q in heading.casefold() or domain_matches)
            # Searching for a ready check must still find its diagnostic area.
            check_matches = bool(q) and category_key in legacy_matches
            topic_rows = matching_topics(search if q and not (heading_matches or check_matches) else '', domain=domain, heading=heading)
            topic_case_ids = {t.case_id for t in topic_rows} if q else set()
            entries = tuple(sorted(
                ((cid, case['title']) for cid, case in cases.items()
                 if case['domain'] == domain
                 and (case['category'] in original_categories or (bool(q) and cid in topic_case_ids))
                 and (not q or heading_matches or check_matches or cid in lookup or cid in topic_case_ids)),
                key=lambda row: (row[1].casefold(), row[0])))
            if entries or topic_rows:
                subjects.append((heading, category_key, entries))
        if subjects:
            result.append((domain, tuple(subjects)))
    return tuple(result)

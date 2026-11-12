"""Build one scan plan from all checked areas, independent of GUI focus."""
from __future__ import annotations
from ..catalog import CATEGORIES


def selected_plan(selections, ready):
    """Every ready, checked pair exactly once, in catalogue order."""
    return tuple((category.key, check.key) for category in CATEGORIES for check in category.checks
                 if check.key in selections.get(category.key, set())
                 and (category.key, check.key) in ready)


# These checks can contact services outside the local machine. A complete
# system scan excludes them unless the user explicitly opts in for this run.
NETWORK_OPT_IN_CHECKS = frozenset({("network", "dns"), ("network", "external")})


def complete_system_plan(ready, *, include_network=False):
    """Run every catalogued local check, once, in a stable order.

    Network checks must be explicitly enabled. No GUI selection or previous
    permission is consulted or persisted. This is a pure scheduling function.
    """
    return tuple(
        (category.key, check.key)
        for category in CATEGORIES
        for check in category.checks
        if (category.key, check.key) in ready
        and (include_network or (category.key, check.key) not in NETWORK_OPT_IN_CHECKS)
    )

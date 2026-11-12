"""Case-specific provisional signal interpretation for sampled events (v77)."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule
from .context_events77 import EVENTS77

OBSERVATION_RULES77 = {
    cid: ObservationRule('context_events77', 'event77_' + cid.replace('.', '_').replace('-', '_'),
                         'observed', 'Gerelateerde lokale gebeurtenis aangetroffen',
                         spec.event, spec.limitation)
    for cid, spec in EVENTS77.items()
}

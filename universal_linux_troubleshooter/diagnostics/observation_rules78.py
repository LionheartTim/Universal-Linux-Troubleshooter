"""v78 deliberately provisional case-to-event mappings, never route approvals."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule
from .context_events78 import EVENTS78, AFTER_SLEEP_CASE, ALL_EVENTS78

OBSERVATION_RULES78 = {
    cid: ObservationRule('context_events78', 'event78_' + cid.replace('.', '_').replace('-', '_'),
                         'observed', 'Brongebonden lokale gebeurtenis aangetroffen',
                         spec.event, spec.limitation)
    for cid,spec in EVENTS78.items()
}
OBSERVATION_RULES78[AFTER_SLEEP_CASE] = ObservationRule(
    'context_events78', 'event78_'+AFTER_SLEEP_CASE.replace('.','_').replace('-','_'),
    'observed', 'Tijdgerelateerde audiogebeurtenis aangetroffen',
    'Na een geregistreerde terugkeer uit slaapstand is binnen 120 seconden een audiofout vastgelegd.',
    'Een temporeel verband bewijst geen oorzakelijkheid, betrokken geluidsuitgang of defect.')
assert set(OBSERVATION_RULES78) == ALL_EVENTS78

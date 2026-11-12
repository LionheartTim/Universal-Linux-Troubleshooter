"""Case-to-event mapping v79; every rule remains provisional and USER_ONLY."""
from __future__ import annotations
from .reviewed_case_rules44 import ObservationRule
from .context_events79 import EVENTS79

OBSERVATION_RULES79 = {
    cid: ObservationRule('context_events79','event79_'+cid.replace('.','_').replace('-','_'),
                         'observed','Specifieke lokale gebeurtenis geregistreerd',
                         spec.event,spec.limitation)
    for cid,spec in EVENTS79.items()
}

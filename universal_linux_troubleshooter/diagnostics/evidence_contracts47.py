"""One audited evidence contract for every documentary case and solution route.

This is an inventory of WHAT must be shown, not an automatic oracle that can
infer an event from prose. The original diagnosis_trees.json stays the single
source for 250 trees and 500 routes. Never silently promote an unreviewed
condition to APPROVED because a check exits with code 0 or produces a warning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Literal

from ..knowledge.diagnosis_trees import load_trees
from .catalog_coverage38 import plan_for_case
from .case_assessment import REVIEWED_ROUTES, APPROVED_ROUTE_STEPS_DIGEST, _route_steps_digest
from .manual_cases40 import _CASE_PROBES
from .physical_connections import guide_for_case

Status = Literal['reviewed_auto_observation', 'experimental_auto_observation', 'needs_case_specific_evidence']


@dataclass(frozen=True)
class RouteRequirement:
    route_id: str
    applicability_condition: str
    user_only: bool
    manual_condition_confirmation: bool
    auto_reviewed: bool
    independent_evidence_required: bool
    steps_fingerprint: str
    verification_goal: str


@dataclass(frozen=True)
class CaseRequirement:
    case_id: str
    domain: str
    title: str
    symptom: str
    possible_cause: str
    supporting_evidence_required: str
    counter_evidence_to_exclude: str
    currently_available_check_ids: tuple[str, ...]
    focused_checks: tuple[str, ...]
    status: Status
    physical_guide: str | None
    routes: tuple[RouteRequirement, ...]
    source_links: tuple[str, ...]
    limitation: str


@lru_cache(maxsize=1)
def all_requirements() -> tuple[CaseRequirement, ...]:
    from .peripheral_rules47 import PERIPHERAL_OBSERVATIONS47
    from .observation_rules50 import OBSERVATION_RULES50
    from .observation_rules51 import OBSERVATION_RULES51
    from .observation_rules52 import OBSERVATION_RULES52
    from .observation_rules59 import OBSERVATION_RULES59
    from .observation_rules61 import OBSERVATION_RULES61
    from .observation_rules62 import OBSERVATION_RULES62
    from .observation_rules63 import OBSERVATION_RULES63
    from .observation_rules64 import OBSERVATION_RULES64
    from .observation_rules65 import OBSERVATION_RULES65
    from .observation_rules66 import OBSERVATION_RULES66
    from .observation_rules67 import OBSERVATION_RULES67
    from .observation_rules77 import OBSERVATION_RULES77
    from .observation_rules78 import OBSERVATION_RULES78
    from .observation_rules79 import OBSERVATION_RULES79
    cases = load_trees()['cases']
    records=[]
    for cid, data in sorted(cases.items()):
        plan = plan_for_case(cid)
        focused = _CASE_PROBES.get(cid, ())
        # New peripheral observations are intentional but NOT yet synthetically
        # and independently validated. Never count as reviewed/approved.
        # A small set has complete synthetic case-and-route review even if
        # the original event mapping was provisional or it uses a standard
        # (not focused) diagnostic check. Neither status is field validation.
        synthetically_reviewed55 = {'network.no-gateway', 'storage.disk-smart'}
        status: Status = ('reviewed_auto_observation' if cid in synthetically_reviewed55
                          else 'experimental_auto_observation' if cid in PERIPHERAL_OBSERVATIONS47 or cid in OBSERVATION_RULES50 or cid in OBSERVATION_RULES51 or cid in OBSERVATION_RULES52 or cid in OBSERVATION_RULES59 or cid in OBSERVATION_RULES61 or cid in OBSERVATION_RULES62 or cid in OBSERVATION_RULES63 or cid in OBSERVATION_RULES64 or cid in OBSERVATION_RULES65 or cid in OBSERVATION_RULES66 or cid in OBSERVATION_RULES67 or cid in OBSERVATION_RULES77 or cid in OBSERVATION_RULES78 or cid in OBSERVATION_RULES79
                          else 'reviewed_auto_observation' if cid in _CASE_PROBES or cid == 'storage.disk-full'
                          else 'needs_case_specific_evidence')
        routes=[]
        for route in data['resolution_routes']:
            rid=route['id']
            proven=(REVIEWED_ROUTES.get(cid,{}).get(rid) == route['applicability_condition']
                    and APPROVED_ROUTE_STEPS_DIGEST.get((cid,rid)) == _route_steps_digest(route['user_steps']))
            routes.append(RouteRequirement(
                rid, route['applicability_condition'],
                route.get('execution')=='USER_ONLY',
                bool(route.get('requires_manual_condition_confirmation',True)),
                proven, not proven,
                _route_steps_digest(route['user_steps']),
                route.get('verification_goal','')
            ))
        guide=guide_for_case(cid)
        records.append(CaseRequirement(
            cid, data['domain'], data['title'], data['symptom'],
            data.get('possible_cause') or '',
            data.get('supporting_evidence') or 'Geen afzonderlijk ondersteunend bewijs beschreven.',
            data.get('counter_evidence') or 'Nog geen expliciet tegenbewijs beschreven.',
            tuple('/'.join(ch) for ch in plan.check_ids), tuple(focused), status,
            guide.kind if guide else None, tuple(routes),
            tuple(data.get('source_links',())),
            ('Bewijsstatus is een technische beoordeling van de beschikbare waarneming, '
             'nooit een bevestiging dat een kabel, poort, driver of component de oorzaak is. '
             'Bij ontbrekende identiteit, tijdstip, tegenbewijs of hertest blijft de route niet bewezen.')))
    return tuple(records)


def coverage_totals() -> dict[str, int]:
    rows=all_requirements()
    routes=[r for row in rows for r in row.routes]
    return {'cases':len(rows), 'routes':len(routes),
            'reviewed_case_signal_rules':sum(r.status=='reviewed_auto_observation' for r in rows),
            'experimental_case_signal_rules':sum(r.status=='experimental_auto_observation' for r in rows),
            'not_yet_case_specific':sum(r.status=='needs_case_specific_evidence' for r in rows),
            'auto_reviewed_route_conditions':sum(r.auto_reviewed for r in routes),
            'pending_route_conditions':sum(r.independent_evidence_required for r in routes),
            'physical_guidance_cases':sum(r.physical_guide is not None for r in rows),
            'cases_missing_possible_cause':sum(not r.possible_cause for r in rows)}


def export_requirements() -> dict:
    return {'schema_version':1, 'purpose':'REVIEW_REQUIREMENTS_NOT_CAUSAL_PROOF',
            'counts':coverage_totals(),
            'review_required_before_ai_training':True,
            'cases':[asdict(x) for x in all_requirements()]}

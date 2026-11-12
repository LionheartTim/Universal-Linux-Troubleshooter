"""Conservative catalog-wide automatic *evidence collection*, not cause inference.

Every one of the 250 documented cases gets a bounded LOCAL check plan. Some
checks are informative only and may not observe the reported symptom. Neither
an AI nor a document can turn this mapping into an executable shell command or
proof of a remedy. No network probe, sudo or automatic repair is supported.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import re
import unicodedata

from ..diagnostics import READY_CHECKS
from ..knowledge.diagnosis_trees import load_trees
from ..results import DiagnosticResult, ResultStatus

_SAFE = frozenset(READY_CHECKS) - {('network','dns'),('network','external')}
_STOP = frozenset(('the','a','an','of','and','with','to','in','or','on','for','is','not','from','after','before','linux',
                    'computer','system','device','app','application','error','issues','issue','problems','problem',
                    'does','can','cannot','fails','failed','failure','working','work','under','when','missing'))

# These are *exploration aids* and never claims that an inferred check can
# validate a specific resolution route. Ordered deliberately, bounded to four.
_GROUPS: dict[str,tuple[tuple[str,str],...]] = {
 'network':(('network','adapter'),('network','ip'),('network','gateway'),('system','system_logs')),
 'storage':(('storage','space'),('storage','drives'),('storage','fs_logs'),('storage','health')),
 'packages':(('system','updates'),('applications','app_crashes'),('system','system_logs')),
 'flatpak':(('applications','app_crashes'),('applications','permissions'),('system','updates')),
 'appimage':(('applications','app_crashes'),('applications','permissions'),('system','system_logs')),
 'audio':(('audio','audio_devices'),('audio','audio_services'),('system','system_logs')),
 'camera':(('system','system_logs'),('hardware','hardware_logs')),
 'bluetooth':(('audio','bluetooth'),('audio','audio_services'),('system','system_logs')),
 'graphics':(('graphics','gpu'),('graphics','render'),('applications','app_crashes')),
 'gpu':(('graphics','gpu'),('graphics','render'),('applications','app_crashes')),
 'display':(('graphics','display'),('graphics','render'),('system','system_logs')),
 'peripherals':(('hardware','hardware_logs'),('system','system_logs')),
 'cpu':(('hardware','sensors'),('hardware','hardware_logs'),('applications','resources')),
 'cooling':(('hardware','sensors'),('hardware','hardware_logs')),
 'board':(('hardware','hardware_logs'),('hardware','sensors'),('system','system_logs')),
 'memory':(('hardware','memory'),('applications','resources'),('hardware','hardware_logs')),
 'power':(('hardware','power'),('hardware','sensors'),('system','system_logs')),
 'hardware':(('hardware','hardware_logs'),('hardware','sensors'),('hardware','memory')),
 'services':(('applications','services'),('system','boot'),('system','system_logs')),
 'boot':(('system','boot'),('applications','services'),('system','system_logs')),
 'system':(('system','system_logs'),('system','boot'),('system','updates')),
 'security':(('applications','permissions'),('system','system_logs')),
 'desktop':(('system','system_logs'),('graphics','render'),('applications','services')),
 'applications':(('applications','app_crashes'),('applications','services'),('applications','resources')),
 'apps':(('applications','app_crashes'),('system','system_logs')),
 'gaming':(('graphics','render'),('applications','resources'),('applications','app_crashes')),
 'virtualization':(('virtualization','vm_backend'),('virtualization','vm_network'),('system','system_logs')),
 'containers':(('virtualization','containers'),('system','system_logs')),
 'development':(('applications','app_crashes'),('system','system_logs')),
 'printing':(('applications','services'),('hardware','hardware_logs')),
 'other':(('system','system_logs'),('hardware','hardware_logs')),
}

@dataclass(frozen=True)
class CatalogPlan:
    case_id: str
    check_ids: tuple[tuple[str,str],...]
    explicit_checks: bool
    interpret_as_cause: bool = False

@lru_cache(maxsize=1)
def _cases():
    return load_trees()['cases']


def plan_for_case(case_id: str, *, max_checks: int = 4) -> CatalogPlan:
    if case_id not in _cases():
        raise KeyError(case_id)
    case=_cases()[case_id]
    declared=[tuple(v.split('/')) for v in case['diagnostic_check_ids']]
    # Additional heuristic checks never take priority over explicitly curated checks.
    group=_GROUPS.get(case['category'], ())
    fallback=(('system','system_logs'),)
    checks=tuple(dict.fromkeys(x for x in (*declared,*group,*fallback) if x in _SAFE))[:max_checks]
    if not checks:
        raise ValueError('No safe available read-only check for ' + case_id)
    return CatalogPlan(case_id,checks,bool(declared))


def coverage_audit() -> dict:
    plans=[plan_for_case(k) for k in _cases()]
    return {'cases':len(plans),
            'with_safe_readonly_candidate':sum(bool(p.check_ids) for p in plans),
            'with_explicit_source_check_ids':sum(p.explicit_checks for p in plans),
            'with_inferred_support_checks_only':sum(not p.explicit_checks for p in plans),
            'automatically_proven_remedies_by_mapping':0,
            'network_checks_scheduled':sum(x in {('network','dns'),('network','external')}
                                            for p in plans for x in p.check_ids)}


def _normal(text: str) -> str:
    return ' '.join(re.findall('[a-z0-9]+',unicodedata.normalize('NFKD',text.casefold())))


def _keywords(text: str) -> set[str]:
    return {x for x in _normal(text).split() if len(x)>=3 and x not in _STOP}


def candidate_case(question: str) -> str | None:
    """Only use an unambiguous documentary match; never present this as diagnosis.

    Future NL/Qwen intent recognition must be validated independently. A vague
    complaint is safer treated as ambiguous than mapped to an unrelated tree.
    """
    if len(question)>4000:
        return None
    q=_normal(question)
    if not q:
        return None
    if question.strip() in _cases():
        return question.strip()
    exact_title=[cid for cid,c in _cases().items() if _normal(c['title'])==q]
    if len(exact_title)==1:
        return exact_title[0]
    if len(exact_title)>1:
        return None
    exact=[]
    for cid,c in _cases().items():
        title=_normal(c['title'])
        if len(title)>12 and (q==title or (' '+title+' ') in (' '+q+' ')):
            exact.append(cid)
    if len(exact)==1:
        return exact[0]
    if len(exact)>1:
        return None
    words=_keywords(q)
    if len(words)<3:
        return None
    scored=[]
    for cid,c in _cases().items():
        title_words=_keywords(c['title'])
        if len(title_words)<3:
            continue
        overlap=len(words & title_words)
        if overlap>=3 and overlap/len(title_words)>=.85:
            scored.append((overlap/len(title_words),overlap,cid))
    scored.sort(reverse=True)
    if scored and (len(scored)==1 or scored[0][:2]>scored[1][:2]):
        return scored[0][2]
    return None


def safe_case_report(case_id: str, results: tuple[DiagnosticResult,...] | list[DiagnosticResult]):
    """Proof-of-collection only. Not even WARNING => confirmed diagnosis.

    Tool outputs are untrusted text, so no log content is re-interpreted here.
    Absence of errors in a bounded window also never disproves a symptom.
    """
    plan=plan_for_case(case_id)
    grouped={}
    for x in results:
        grouped.setdefault(f'{x.category_key}/{x.check_key}',[]).append(x)
    checks={k:v[0] for k,v in grouped.items() if len(v)==1}
    completed=[]; unavailable=[]; observations=[]
    for area,key in plan.check_ids:
        cid=f'{area}/{key}'
        r=checks.get(cid)
        if r is None or r.status in (ResultStatus.UNKNOWN,ResultStatus.NOT_RUN):
            unavailable.append(cid)
        else:
            completed.append(cid)
            # Checkers own this bounded statement. Do not repeat untrusted raw
            # journal text, infer a cause or ask the user to analyze logs.
            observations.append((cid,r.status.value,r.diagnosis[:160]))
    return {
        'case_id':case_id,
        'title':_cases()[case_id]['title'],
        'completed':tuple(completed),
        'unavailable':tuple(unavailable),
        'observations':tuple(observations),
        'diagnosis':'unknown',
        'route':None,
        'linked_alternatives':tuple(_cases()[case_id]['cross_domain_case_ids']),
        'reason':'Checks can find clues, but no case-specific validated cause/route assessor exists yet.',
    }


def safe_general_report(results: list[DiagnosticResult] | tuple[DiagnosticResult,...]) -> str:
    """Describe real check outcomes without requiring an LLM or user log review."""
    completed=[r for r in results if r.status not in (ResultStatus.UNKNOWN,ResultStatus.NOT_RUN)]
    lines=[f'De Troubleshooter heeft {len(completed)} van {len(results)} lokale controles uitgevoerd met leesbare resultaten.']
    for r in completed[:5]:
        lines.append(f'- {r.category_key}/{r.check_key} ({r.status.value}): {r.diagnosis[:170]}')
    incomplete=len(results)-len(completed)
    if incomplete:
        lines.append(f'{incomplete} controle(s) waren niet uitvoerbaar of gaven onvoldoende gegevens. Dit betekent niet dat die onderdelen gezond zijn.')
    lines.append('Deze resultaten zijn aanwijzingen, geen onafhankelijk bewezen oorzaak. Er wordt niets gerepareerd of gewijzigd. Het diagnoseonderzoek blijft bij de Troubleshooter, niet bij de gebruiker.')
    return '\n'.join(lines)

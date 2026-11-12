"""Manual Diagnostics case picker and evidence report (NO AI, NO repairs).

The 250 descriptions are documentary scope, not 250 proven diagnoses.
Only explicitly reviewed case assessors may select documented solution routes.
The user chooses a symptom; the app collects available local evidence itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from ..knowledge.diagnosis_trees import load_trees
from ..results import DiagnosticResult, ResultStatus
from .catalog_coverage38 import plan_for_case
from .case_assessment import assess_case_id
from .reviewed_case_rules44 import OBSERVATION_RULES
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
from .physical_connections import guide_for_case
from .context_intake68 import context_explanation
from .guided_evidence74 import CASES74, SAFE_FOLLOWUPS74
from .triage_guidance53 import followup_for_case
from .topic_catalog127 import guide_for_topic

# Allowlisted fixed in code; neither a document nor a model can introduce a probe.
_SEARCH_ALIASES = {
    'software35.applications.gpu-vs-app-interference': ('deepcool', 'mystique', 'gpu app'),
    'network.wired-link-no-carrier': ('ethernet', 'netwerkkabel', 'dhcp'),
    'software35.network.dns-per-app': ('flatpak dns', 'sandbox internet'),
    'peripherals.usb-not-recognized': ('usb poort', 'andere usb poort', 'usb cable', 'usb kabel'),
    'hardware34.peripherals.usb-descriptor': ('usb poort', 'usb kabel', 'other usb port'),
}

_CASE_PROBES = {
    'network.wired-link-no-carrier': ('dhcp',),
    'software35.boot.wrong-kernel-after-update': ('atomic_pending',),
    'hardware34.storage.nvme-critical-warning': ('nvme',),
    'software35.services.high-boot-time': ('boot_phases',),
    'software35.network.dns-per-app': ('app_dns',),
    'software35.applications.gpu-vs-app-interference': ('gpu_app',),
    # Specific validated observation sources; generic catalog checks remain
    # exploratory only and can never independently authorize a repair.
    'network.wifi-missing': ('radio_blocks',),
    'audio.bluetooth-not-found': ('radio_blocks',),
    'hardware.memory-error': ('kernel_signals',),
    'hardware34.memory.ecc-uncorrected': ('kernel_signals',),
    'graphics.gpu-crash': ('kernel_signals',),
    'hardware34.gpu.physical-reset': ('kernel_signals',),
    'storage.filesystem-errors': ('kernel_signals',),
    'software35.services.oom-killed': ('kernel_signals',),
    'system.oom-killed': ('kernel_signals',),
    'applications.service-failed': ('failed_units',),
    'system.failed-service': ('failed_units',),
    'system.service-restarts': ('failed_units',),
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES.items()},
    **{cid:(rule.probe,) for cid,rule in PERIPHERAL_OBSERVATIONS47.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES50.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES51.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES52.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES59.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES61.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES62.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES63.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES64.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES65.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES66.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES67.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES77.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES78.items()},
    **{cid:(rule.probe,) for cid,rule in OBSERVATION_RULES79.items()},
}


@lru_cache(maxsize=1)
def case_catalog():
    return load_trees()['cases']


def browse_cases(*, domain: str = 'all', search: str = '') -> tuple[tuple[str, str, str], ...]:
    """Search explicit case titles/IDs without guessing the user's diagnosis."""
    if domain not in ('all', 'hardware', 'software'):
        raise ValueError('Unknown diagnosis domain')
    term = search.strip().casefold()[:150]
    return tuple(sorted(
        ((cid, case['title'], case['domain']) for cid, case in case_catalog().items()
         if (domain == 'all' or case['domain'] == domain)
         and (not term or term in case['title'].casefold() or term in cid.casefold()
              or term in case['symptom'].casefold()
              or any(term in alias for alias in _SEARCH_ALIASES.get(cid, ())))),
        key=lambda entry: (entry[2], entry[1].casefold(), entry[0])))


def plan_for_manual_case(case_id: str) -> tuple[tuple[tuple[str, str], ...], tuple[str, ...]]:
    """Generate strictly local, allowlisted checks; never run manual commands."""
    plan = plan_for_case(case_id)
    return plan.check_ids, _CASE_PROBES.get(case_id, ())


@dataclass(frozen=True)
class CaseView:
    case_id: str
    title: str
    status: str
    diagnosis: str
    solution: str
    evidence: str
    related: tuple[tuple[str, str], ...]
    proven_route: str | None
    physical_check: bool = False


def present_case(case_id: str, results: Sequence[DiagnosticResult], *, completed: bool = True, topic_id: str | None = None, target_note: str | None = None, target_inventory: DiagnosticResult | None = None, guided_result74: DiagnosticResult | None = None, network_result75: DiagnosticResult | None = None) -> CaseView:
    """Format a completed run without pretending a generic warning proves a cause.

    A targeted reviewed assessor can select a route, but only if the frozen
    applicability condition still agrees with the original validated catalog.
    Unreviewed cases always stop at unknown and do not expose speculative fixes.
    """
    case = case_catalog()[case_id]
    topic = guide_for_topic(topic_id, case_id) if topic_id else None
    plan_checks, probe_keys = plan_for_manual_case(case_id)
    expected = set(plan_checks) | {('focused', k) for k in probe_keys}
    # Ignore stale, unrelated, duplicated and forged rows. A duplicate is
    # treated as unavailable; the user must never get an arbitrary winner.
    actual: dict[tuple[str, str], list[DiagnosticResult]] = {}
    for r in results:
        if (r.category_key, r.check_key) in expected:
            actual.setdefault((r.category_key, r.check_key), []).append(r)
    unique = [v[0] for k, v in actual.items() if len(v) == 1]
    # The route assessor is further restricted to the exact reviewed evidence
    # needs, never a heuristic background check or raw journal text.
    finding = assess_case_id(case_id, unique)
    valid = [(k, actual[k][0]) for k in (*plan_checks, *(('focused', x) for x in probe_keys))
             if k in actual and len(actual[k]) == 1]
    missing = [k for k in (*plan_checks, *(('focused', x) for x in probe_keys))
               if k not in actual or len(actual[k]) != 1
               or actual[k][0].status in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN)]
    findings = [f'{a}/{b}: {r.diagnosis[:220]}' for (a,b),r in valid
                if r.status not in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN) and a != 'focused']
    lines = [finding.conclusion]
    if not completed:
        lines.insert(0, 'Het onderzoek is afgebroken of nog niet volledig uitgevoerd. Er volgt geen oplossingsadvies.')
    lines.extend('• ' + item for item in finding.proof)
    lines.extend('• Nog niet vastgesteld: ' + item for item in finding.limitations)
    if finding.symptom == 'contradicted':
        lines.append('De beschikbare gegevens ondersteunen deze specifieke verklaring niet. Andere oorzaken zijn mogelijk.')
    elif finding.symptom == 'unknown':
        lines.append('De oorzaak is nog niet voldoende bewezen. Er wordt geen oplossing op basis van een gok voorgesteld.')
    if findings:
        lines.append('Andere lokaal waargenomen signalen (geen bewijs voor een oorzaak):')
        lines.extend('• ' + item for item in findings[:4])
    if missing:
        lines.append('Niet betrouwbaar beschikbaar: ' + ', '.join('/'.join(pair) for pair in missing))
    route = None
    if finding.route:
        # The case assessor has independently verified the route condition.
        route = next((r for r in case['resolution_routes'] if r['id'] == finding.route), None)
    if not completed:
        route = None
    if route is not None and finding.symptom == 'supported':
        instruction = ('Een passende oplossingsrichting is gevonden. Voer een wijziging uitsluitend zelf uit, '
                       'nadat je de gevolgen begrijpt. De Troubleshooter verandert niets.\n'
                       + 'Voorwaarde: ' + route['applicability_condition'] + '\n'
                       + '\n'.join(f'{index}. {step}' for index,step in enumerate(route['user_steps'],1))
                       + '\nControleer na afloop of het oorspronkelijke probleem echt verdwenen is.')
        if finding.solution_kind == 'package':
            instruction += ('\nVoor pakketbeheer: kies de gebruiksvriendelijke Universal Linux Software Manager '
                            'via de Info-tab. Voor uitleg over opdrachten: Universal Linux Terminal via de Info-tab. '
                            'Behoud de oorspronkelijke pakketbron en voer nooit blind commando’s uit.')
    else:
        instruction = ('Nog geen gevalideerde reparatieroute. De Troubleshooter voert geen wijzigingen uit, '
                       'en vraagt je niet zelf logboeken te vergelijken. '\
                       'Aanvullend onderzoek of een toekomstige gevalideerde bewijsregel is nodig.')
    # Every case has two source-authored conditional routes. Explain what is
    # still being investigated WITHOUT displaying their repair instructions
    # or treating their mere presence as evidence. Safe for Manual mode, and
    # fully independent of Qwen and arbitrary shell execution.
    if route is None and completed:
        conditions = [r['applicability_condition'] for r in case['resolution_routes']]
        instruction += ('\n\nMogelijke onderzoekspaden uit de diagnoseboom '
                        '(GEEN bewezen oorzaak of goedgekeurde reparatie):\n'
                        + '\n'.join(f'• {condition}' for condition in conditions)
                        + '\nAlleen wanneer de specifieke voorwaarde onafhankelijk is aangetoond, '
                          'mag de bijbehorende oplossing worden overwogen. '
                          'Gebruik Rescan na een veilige handeling; een lege log bewijst geen herstel.')
    # A useful next step is not synonymous with a proven repair. These
    # user-only, case-scoped notes never authorize commands or route selection.
    # They are suppressed for cancelled scans and whenever a reviewed solution
    # route already applies.
    if route is None and completed:
        followups = followup_for_case(case_id, completed=True)
        if followups:
            instruction += ('\n\nVeilige vervolgstap (geen bewezen oorzaak of reparatie):\n'
                            + '\n'.join(f'{i}. {line}' for i, line in enumerate(followups, 1)))
    if completed and not route:
        from .guided_evidence80 import APPIMAGE_CASE80
        context = ('An AppImage was selected privately for an optional, read-only checksum comparison. '
                   'A user-supplied hash is not independent proof of its official source; no path or hash is logged.'
                   if case_id == APPIMAGE_CASE80 else context_explanation(case_id, target_note))
        if context:
            instruction += '\n\n' + context
        # A target-scoped inventory observation NEVER changes the assessed
        # symptom or route. It is merely a local identification aid, and is
        # intentionally not copied into technical evidence logs.
        if (target_inventory is not None and target_inventory.category_key == 'focused'
                and target_inventory.check_key == 'target_inventory69'
                and target_inventory.status in (ResultStatus.INFO, ResultStatus.UNKNOWN)):
            instruction += ('\n\nGerichte lokale identificatie (geen oorzaaksbewijs):\n'
                            + target_inventory.explanation[:550])
    # v81: evidence-acceptance plan for the final ten context cases.
    # This is never inserted as FACT evidence or treated as a route.
    if completed and route is None:
        from .verification_protocols81 import explain_unverified81
        protocol81 = explain_unverified81(case_id)
        if protocol81:
            instruction += '\n\nGericht verificatieprotocol (dossier nog OPEN):\n' + protocol81
    # v74 independent local observations: never a cause, FACT or route. No
    # unsigned probe may override the strict 15 reviewed route conditions.
    if (completed and guided_result74 is not None
            and case_id in CASES74
            and guided_result74.category_key == 'focused'
            and guided_result74.check_key == 'guided_evidence74'
            and guided_result74.status in (ResultStatus.INFO, ResultStatus.UNKNOWN)):
        lines.append('Gerichte lokale waarneming (geen bewezen oorzaak): ' + guided_result74.explanation[:800])
        if route is None:
            instruction += ('\n\nGerichte veilige vervolgstappen (GEEN vrijgegeven reparatieroute):\n'
                            + SAFE_FOLLOWUPS74[case_id])
    # v75 opt-in network observations are never promoted to FACT evidence or
    # trusted route approval. The GUI must not expose untrusted target bytes.
    from .consented_network75 import NETWORK_CASES75
    if (completed and network_result75 is not None and case_id in NETWORK_CASES75
            and network_result75.category_key == 'focused'
            and network_result75.check_key == 'consented_dns75'
            and network_result75.status in (ResultStatus.INFO, ResultStatus.UNKNOWN)):
        lines.append('Optionele netwerkvergelijking (geen bewezen oorzaak): ' + network_result75.explanation[:800])
        if route is None:
            instruction += ('\n\nVeilig vervolg na optionele netwerkvergelijking (geen reparatievrijgave):\n'
                            + 'Controleer de doelnaam en de gebruikte dienst. Verander geen DNS- of hosts-instellingen '
                              'zonder onafhankelijk bevestigd bewijs. Gebruik Rescan na een wijziging.')
    # Optional beginner-friendly *physical isolation check*, not an automatic
    # resolution route. Unlike evidence gating this needs the user's hands,
    # but no diagnostic command/log comparison or unapproved app action.
    physical = (guide_for_case(case_id) if completed and topic is None
                and not (case_id == 'network.wired-link-no-carrier' and finding.route == 'route_2')
                else None)
    if topic is not None and completed:
        instruction += ('\n\nEen veilige, apparaatgerichte vervolgstap (GEEN bewezen defect of reparatie):\n\n'
                        + topic.describe())
    if physical is not None:
        instruction += ('\n\nEr is wel een veilige fysieke vervolgstap voor deze aansluiting. '
                        'Dit is geen vastgestelde reparatie en vraagt geen logonderzoek van de gebruiker.'
                        '\n\n' + physical.describe())
    related = tuple((cid, case_catalog()[cid]['title']) for cid in case['cross_domain_case_ids'])
    evidence = ['Alleen-lezenonderzoek; geen AI en geen reparaties. Optionele gerichte netwerkcheck uitsluitend na afzonderlijke toestemming.',
                f'Dossier: {case_id}', f'Controles gepland: {len(plan_checks)} reguliere + {len(probe_keys)} aanvullende.']
    for (a,b),r in valid:
        evidence.extend((f'{a}/{b} [{r.status.value}] {r.explanation[:240]}',
                         *(f'  {line[:240]}' for line in r.evidence[:6] if not line.startswith('FACT:'))))
    if missing:
        evidence.append('Niet beschikbaar of onzeker: ' + ', '.join('/'.join(k) for k in missing))
    return CaseView(case_id, topic.title if topic else case['title'], finding.symptom if completed else 'unknown',
                    '\n'.join(lines), instruction, '\n'.join(evidence),related,
                    finding.route if route else None, (physical is not None or (topic is not None and completed)))

"""Read-only access and deterministic traversal of the unified diagnosis-tree data.

This deliberately does not execute *any* commands, run checkers, import the
AI engine, probe networks, modify the OS, or infer truth from raw log text.
The case file is documentation until explicitly integrated and reviewed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ..catalog import CATEGORIES

DATA_FILE = Path(__file__).resolve().parents[2] / 'knowledge_sources' / 'diagnosis_trees.json'
APPROVED_CHECK_IDS = frozenset(
    f'{cat.key}/{check.key}' for cat in CATEGORIES for check in cat.checks
)
NETWORK_OPT_IN_IDS = frozenset({'network/dns', 'network/external'})


class InvalidTree(ValueError):
    """Invalid graph or invalid user-supplied navigation decision."""


@dataclass(frozen=True)
class NextNode:
    case_id: str
    node: Mapping[str, Any]
    human_choice_required: bool


def load_trees(path: Path | str | None = None) -> dict:
    """Parse the single documented catalog; never use eval or import data as code."""
    with Path(path or DATA_FILE).open(encoding='utf-8') as fd:
        catalog = json.load(fd)
    validate_trees(catalog)
    return catalog


def validate_trees(catalog: Mapping[str, Any]) -> None:
    if catalog.get('schema_version') != 2:
        raise InvalidTree('Unsupported diagnosis-tree schema')
    if catalog.get('scope') != 'DATA_AND_READ_ONLY_TRAVERSAL_ONLY':
        raise InvalidTree('Missing read-only contract')
    cases = catalog.get('cases')
    if not isinstance(cases, dict) or not cases:
        raise InvalidTree('No case trees')
    count = 0
    for domain in ('hardware', 'software'):
        ids = catalog['domains'][domain]
        if len(ids) != len(set(ids)) or any(cid not in cases or cases[cid]['domain'] != domain for cid in ids):
            raise InvalidTree(f'Bad {domain} index')
        count += len(ids)
    if count != len(cases):
        raise InvalidTree('Case missing from domain index')
    if catalog['counts'].get('total') != len(cases):
        raise InvalidTree('Invalid total count')
    if set(catalog['domains']['hardware']) | set(catalog['domains']['software']) != set(cases):
        raise InvalidTree('A case is missing from its declared domain')
    if set(catalog['domains']['hardware']) & set(catalog['domains']['software']):
        raise InvalidTree('A case cannot appear in both domains')
    expected_contract = {'repair_actions': 'USER_ONLY',
                         'missing_evidence': 'UNKNOWN_NOT_NEGATIVE',
                         'ai_training': 'DISABLED',
                         'ui_integration': 'READ_ONLY_MANUAL_PRESENTATION',
                         'evidence_question': 'SYMPTOM_CONFIRMATION_ONLY_NOT_CAUSE_PROOF',
                         'route_evidence_question': 'INDEPENDENT_MANUAL_CONFIRMATION_FOR_EACH_ROUTE'}
    if any(catalog.get('safety_contract', {}).get(k) != v for k,v in expected_contract.items()):
        raise InvalidTree('Evidence or read-only safety contract mismatch')
    edges = set()
    for entry in catalog.get('cross_domain_links', []):
        a,b = entry['from'],entry['to']
        if a not in cases or b not in cases or a == b or cases[a]['domain'] == cases[b]['domain']:
            raise InvalidTree('Broken cross-domain link')
        if b not in cases[a]['cross_domain_case_ids'] or a not in cases[b]['cross_domain_case_ids']:
            raise InvalidTree('Asymmetric cross-domain link')
        edge = tuple(sorted((a,b)))
        if edge in edges:
            raise InvalidTree('Duplicate cross-domain link')
        edges.add(edge)
    if catalog['counts']['cross_domain_undirected_links'] != len(edges):
        raise InvalidTree('Invalid cross-domain link count')
    for cid,case in cases.items():
        if case['id'] != cid or case['domain'] not in ('hardware','software'):
            raise InvalidTree(f'Case identity invalid: {cid}')
        if case.get('execute_commands') is not False or case.get('ai_training_enabled') is not False:
            raise InvalidTree(f'Unsafe execution/training flag: {cid}')
        for linked in case['cross_domain_case_ids']:
            if tuple(sorted((cid,linked))) not in edges:
                raise InvalidTree(f'Undocumented cross-link {cid} -> {linked}')
        if any(check not in APPROVED_CHECK_IDS for check in case['diagnostic_check_ids']):
            raise InvalidTree(f'Non-allowlisted diagnostic ID in {cid}')
        if any(command.get('runtime_approved') is not False or command.get('display_only') is not True
               for command in case['manual_diagnostic_commands'] + case['retest_commands']):
            raise InvalidTree(f'Executable document command in {cid}')
        nodes = case['tree']['nodes']
        index = {n['id']:n for n in nodes}
        if len(index) != len(nodes) or case['tree']['entry_node'] != 'start' or 'start' not in index:
            raise InvalidTree(f'Duplicate/missing node in {cid}')
        if len(nodes) != 8 + 3*len(case['resolution_routes']):
            raise InvalidTree(f'Unexpected number of route assessment nodes in {cid}')
        for n in nodes:
            successors = list(n.get('branches', {}).values()) + ([n['next']] if 'next' in n else [])
            if any(x not in index for x in successors):
                raise InvalidTree(f'Invalid edge in {cid}/{n["id"]}')
            if n['type'] == 'manual_resolution' and n['execution'] != 'USER_ONLY':
                raise InvalidTree(f'Unsafe resolution: {cid}/{n["id"]}')
            if n['type'] == 'collect_evidence' and n['runtime_allowed_command_execution'] is not False:
                raise InvalidTree(f'Unsafe collection node: {cid}')
            if n['type'] == 'decision' and n['requires_manual_evidence_confirmation'] is not True:
                raise InvalidTree(f'Unchecked evidence claim: {cid}/{n["id"]}')
        expected_route_ids = {x['id'] for x in case['resolution_routes']}
        if not expected_route_ids or not expected_route_ids.issubset(index):
            raise InvalidTree(f'No reachable manual routes in {cid}')
        if set(index['select_route']['branches']) != expected_route_ids | {'none_match'}:
            raise InvalidTree(f'Route selector mismatch: {cid}')
        if index['select_route']['branches']['none_match'] != 'alternatives':
            raise InvalidTree(f'Invalid none_match handling: {cid}')
        if (index['evidence'].get('evidence_semantics') != 'SYMPTOM_ONLY_NOT_ROUTE_OR_CAUSE'
                or index['evidence'].get('branches') != {
                    'supported':'select_route','contradicted':'alternatives','unknown':'more_evidence'}):
            raise InvalidTree(f'Symptom gate mislabeled or unsafe: {cid}')
        if not case.get('symptom') or not case.get('supporting_evidence'):
            raise InvalidTree(f'Missing symptom or evidence clues: {cid}')
        for route in case['resolution_routes']:
            rid = route['id']; aid = f'assess_{rid}'; vid = f'verify_{rid}'
            assessment = index.get(aid)
            manual = index.get(rid)
            verification = index.get(vid)
            if (not assessment or assessment.get('type')!='decision'
                    or assessment.get('route_id') != rid
                    or not route.get('applicability_condition')
                    or assessment.get('route_condition') != route['applicability_condition']
                    or assessment.get('evidence_semantics') != 'ROUTE_CONDITION_ONLY'
                    or assessment.get('branches') != {
                        'supported':rid,'contradicted':'select_route','unknown':'more_evidence'}
                    or index['select_route']['branches'].get(rid) != aid
                    or not manual or manual.get('type') != 'manual_resolution'
                    or manual.get('condition') != route['applicability_condition']
                    or manual.get('execution') != 'USER_ONLY'
                    or manual.get('next') != vid
                    or not verification or verification.get('branches') != {
                        'resolved':'resolved','not_resolved':'retry_routes','unknown':'more_evidence'}):
                raise InvalidTree(f'Unprotected or inconsistent resolution route: {cid}/{rid}')
        if (index['retry_routes'].get('branches') != {
                'another_condition_confirmed':'select_route',
                'no_other_condition':'alternatives','unknown':'more_evidence'}
                or index['more_evidence'].get('type')!='insufficient_evidence'
                or index['more_evidence'].get('terminal') is not True
                or index['resolved'].get('type') != 'resolved_after_retest'
                or index['resolved'].get('terminal') is not True):
            raise InvalidTree(f'Invalid unknown, retry, or retest behavior: {cid}')
        # Follow the directed tree, not just node existence.
        seen = set()
        todo = [case['tree']['entry_node']]
        while todo:
            curr = todo.pop()
            if curr in seen:
                continue
            seen.add(curr)
            n = index[curr]
            todo.extend(n.get('branches', {}).values())
            if 'next' in n:
                todo.append(n['next'])
        if len(seen) != len(index):
            raise InvalidTree(f'Unreachable nodes: {cid}: {sorted(set(index)-seen)}')


def get_node(catalog: Mapping[str,Any], case_id: str, node_id: str='start') -> NextNode:
    """Read one node; no case selection inference is performed."""
    case = catalog['cases'][case_id]
    node = next((n for n in case['tree']['nodes'] if n['id'] == node_id), None)
    if node is None:
        raise InvalidTree(f'No such node: {case_id}/{node_id}')
    return NextNode(case_id, node, node['type'] == 'decision')


def advance(catalog: Mapping[str,Any], case_id: str, node_id: str,
            *, choice: str | None = None, confirmed_by_user: bool = False) -> NextNode:
    """Traverse one edge. Explicit choices never imply automatically confirmed facts.

    For decision nodes, only an explicit human-confirmed choice is accepted.
    For automatic NEXT edges, this function merely advances the document cursor.
    """
    current = get_node(catalog,case_id,node_id).node
    if current['type']=='decision':
        if not confirmed_by_user:
            raise InvalidTree('User must confirm decision evidence or route applicability')
        if choice not in current['branches']:
            raise InvalidTree(f'Invalid choice for {case_id}/{node_id}: {choice!r}')
        target = current['branches'][choice]
    elif 'next' in current:
        if choice is not None:
            raise InvalidTree('This node has no manual choices')
        target = current['next']
    else:
        raise InvalidTree('End of this diagnostic path')
    return get_node(catalog,case_id,target)


def follow_cross_domain(catalog: Mapping[str,Any], case_id: str, node_id: str,
                        destination_id: str, *, confirmed_by_user: bool = False) -> NextNode:
    """Explicitly move to the start of a *curated* linked tree.

    Merely appearing in the catalog is not evidence of a shared root cause.
    All transitions require a human choice at an alternative-evidence node.
    """
    src = get_node(catalog,case_id,node_id).node
    if src['type'] not in ('investigate_alternatives','insufficient_evidence'):
        raise InvalidTree('Cross-domain transition only allowed from alternatives/evidence gap')
    if not confirmed_by_user:
        raise InvalidTree('Cross-domain investigation requires user confirmation')
    if destination_id not in src['cross_domain_case_ids']:
        raise InvalidTree('Not a curated cross-domain link')
    return get_node(catalog,destination_id)

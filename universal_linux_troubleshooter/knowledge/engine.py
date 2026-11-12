"""One offline, shared troubleshooting planner for all diagnostic categories.

A symptom is only a search clue, NEVER proof of a root cause. The planner
selects existing read-only checks; the assessor combines their actual results.
No database content is ever executed as shell commands or downloaded at runtime.
"""
from __future__ import annotations
from dataclasses import dataclass
from contextlib import contextmanager
import json
from importlib.resources import files
import re
import sqlite3
from pathlib import Path
from typing import Mapping

from ..catalog import CATEGORIES
from ..results import DiagnosticResult, ResultStatus
from ..diagnostics.plan import NETWORK_OPT_IN_CHECKS

STOP = frozenset('the a an my is are i have and or with on in of to why how computer pc linux laptop system it een het de mijn dat er bij kan does problem problemen probleem please help'.split())
GENERIC = frozenset('not no work fail error issue cannot problem miss start stop broken bad please'.split())
TOKEN = re.compile(r'[^\W_]+', re.UNICODE)
CANON = {'disconnecting':'disconnect','disconnected':'disconnect','disconnections':'disconnect',
 'fails':'fail','failed':'fail','failing':'fail','failure':'fail','crashed':'crash',
 'crashes':'crash','crashing':'crash','booting':'boot','boots':'boot',
 'updating':'update','updates':'update','connection':'connect','connected':'connect','freezes':'freeze','freezing':'freeze','frozen':'freeze',
 'connectivity':'connect','connections':'connect','shuts':'shutdown',
 'shutdowns':'shutdown','missing':'miss','misses':'miss','problems':'problem',
 'working':'work','works':'work','wont':'not','refuses':'fail'}


def tokens(value: str) -> frozenset[str]:
    words=TOKEN.findall(value.casefold().replace('wi-fi','wifi'))
    return frozenset(CANON.get(x,x) for x in words if len(x)>1 and x not in STOP)



@dataclass(frozen=True)
class KnowledgeItem:
    id: str
    category: str
    title: str
    phrases: tuple[str, ...]
    possible_cause: str
    checks: tuple[tuple[str, str], ...]
    evidence_hints: tuple[str, ...]
    steps: tuple[str, ...]
    sources: tuple[str, ...]
    review_status: str


@dataclass(frozen=True)
class SolutionRoute:
    id: str
    problem_id: str
    title: str
    when_to_use: str
    steps: tuple[str, ...]
    verification: str
    safety: str
    review_status: str


@dataclass(frozen=True)
class FoundItem:
    item: KnowledgeItem
    score: float


class KnowledgeBase:
    def __init__(self, path: str | Path | None = None):
        # SQLite is opened strictly read-only. It is a bundled offline seed;
        # nothing in the app downloads or updates knowledge by itself.
        if path is None:
            path = files('universal_linux_troubleshooter').joinpath('knowledge/problems.sqlite3')
        self.path = Path(str(path))

    @contextmanager
    def _open(self):
        con = sqlite3.connect(self.path.resolve().as_uri() + '?mode=ro', uri=True)
        con.row_factory = sqlite3.Row
        try:
            yield con
        finally:
            con.close()

    def solution_routes(self, problem_id: str) -> tuple[SolutionRoute, ...]:
        """Read alternate, conditioned manual routes for a validated DB case."""
        with self._open() as con:
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='solution_routes'").fetchone():
                return ()
            rows = con.execute('SELECT * FROM solution_routes WHERE problem_id=? ORDER BY route_order',
                               (problem_id,)).fetchall()
        return tuple(SolutionRoute(row['id'],row['problem_id'],row['title'],row['when_to_use'],
                       tuple(json.loads(row['steps'])),row['verification'],row['safety'],row['review_status']) for row in rows)

    def count(self) -> int:
        with self._open() as con:
            return con.execute('SELECT count(*) FROM problems').fetchone()[0]

    @staticmethod
    def _item(row) -> KnowledgeItem:
        return KnowledgeItem(row['id'], row['category'], row['title'],
            tuple(p.strip() for p in row['phrases'].split('|')),
            row['possible_cause'], tuple(tuple(pair) for pair in json.loads(row['checks'])),
            tuple(json.loads(row['evidence_hints'])), tuple(json.loads(row['steps'])),
            tuple(json.loads(row['sources'])), row['review_status'])

    def search(self, symptom: str, *, limit: int = 6) -> tuple[FoundItem, ...]:
        query = symptom.strip()[:512]
        qt = tokens(query)
        if not qt:
            return ()
        with self._open() as con:
            # SQLite FTS5 narrows candidate documents before the independent
            # relevance ranker. Never interpolate unsanitized user text in SQL.
            index_terms = [t for t in sorted(qt) if re.fullmatch(r'[a-z0-9]{2,40}', t)][:14]
            try:
                ids = [row[0] for row in con.execute(
                    'SELECT id FROM problem_fts WHERE problem_fts MATCH ? LIMIT 300',
                    (' OR '.join(term + '*' for term in index_terms),))] if index_terms else []
                if ids:
                    marks = ','.join('?' for _ in ids)
                    rows = con.execute(f'SELECT * FROM problems WHERE id IN ({marks}) ORDER BY id', ids).fetchall()
                else:
                    # Missing FTS extension or unindexed language: safe fallback.
                    rows = con.execute('SELECT * FROM problems ORDER BY id').fetchall()
            except sqlite3.OperationalError:
                rows = con.execute('SELECT * FROM problems ORDER BY id').fetchall()
        found = []
        query_lower = query.casefold().replace('wi-fi', 'wifi')
        query_plain = re.sub(r'^(?:the|my|a|an|our)\s+', '', query_lower)
        for row in rows:
            item = self._item(row)
            title_tokens = tokens(item.title)
            # Phrase matching is a strong indicator of user intent, but it is
            # NEVER used as evidence that a computer component is defective.
            phrases = tuple(p.casefold().replace('wi-fi','wifi') for p in item.phrases)
            exact = max((len(tokens(p)) for p in phrases if p and len(tokens(p)) >= 2 and p in query_lower), default=0)
            phrase_score = 0.0
            for phrase in phrases:
                pt = tokens(phrase)
                matched = len(qt & pt)
                if pt and matched:
                    # Two matching technical words usually beat generic titles.
                    score = 2.5 * matched * matched / max(len(pt), 1)
                    if matched == len(pt): score += 3.0
                    phrase_score = max(phrase_score, score)
            overlap = len(qt & title_tokens)
            meaningful = qt & tokens(item.title + ' ' + ' '.join(item.phrases)) - GENERIC
            if not meaningful:
                continue
            # A single common word such as 'wifi' or 'failed' must not cause
            # unrelated cases to appear; prefer specific phrase/title matches.
            title_exact = len(query_plain) >= 8 and query_plain in item.title.casefold()
            score = 7.0 * bool(exact) + 2.0 * exact + phrase_score + 2.0 * overlap + 8.0 * title_exact
            if (exact or title_exact or overlap >= 2 or (phrase_score >= 6.0 and len(qt) >= 2)) and score >= 6.0:
                found.append(FoundItem(item, round(score, 2)))
        found.sort(key=lambda x: (-x.score, x.item.id))
        # Only keep reasonably related candidates; a weak match should not
        # trigger unnecessary tests in an unrelated category.
        if found:
            threshold = max(6.0, found[0].score * 0.55)
            found = [m for m in found if m.score >= threshold]
        return tuple(found[:max(1,min(limit,20))])


@dataclass(frozen=True)
class InvestigationPlan:
    question: str
    matches: tuple[FoundItem, ...]
    checks: tuple[tuple[str, str], ...]
    skipped_online: tuple[tuple[str, str], ...]


class TroubleshootingEngine:
    def __init__(self, knowledge: KnowledgeBase | None = None):
        self.knowledge = knowledge or KnowledgeBase()

    def automatic_guidance(self, result: DiagnosticResult,
                           results: Mapping[tuple[str, str], DiagnosticResult] | None = None) -> AutomaticGuidance | None:
        """Consult all relevant database cases for every diagnosis/solution.

        A status of OK, INFO, NOT RUN or UNKNOWN is *not* positive evidence.
        For WARNING/PROBLEM, require a recorded concrete clue in at least one
        matching check (not a symptom, explanatory warning or mere database hit).
        Never suggest changing a system based solely on a weak log-text match.
        """
        if result.status not in (ResultStatus.WARNING, ResultStatus.PROBLEM):
            return None
        key = (result.category_key, result.check_key)
        try:
            candidates = _load_items_for_engine(self).get(key, ())
        except (OSError, sqlite3.Error):
            # Missing optional data must never break the normal diagnosis GUI.
            return None
        if not candidates:
            return None
        context = dict(results or {})
        context[key] = result
        possibilities = []
        for item in candidates:
            matching = []
            specificity = 0
            for pair in item.checks:
                observed = context.get(pair)
                if not observed or observed.status not in (ResultStatus.WARNING, ResultStatus.PROBLEM):
                    continue
                # A group label or an event count is NOT a failed component.
                # Require the actual observation mentioning a clue to describe a
                # concrete trouble signal, rather than merely naming hardware.
                signals = ('fail', 'error', 'denied', 'timeout', 'disconnect', 'crash',
                           'reset', 'low space', 'low memory', 'no address', 'no route',
                           'no default', 'under 2 gib', 'under 10%', 'unavailable',
                           'corrupt', 'refused', 'deauth', 'thermal', 'overheat',
                           'oom', 'not found', 'not detected', 'no space', 'missing',
                           'critical', 'prefail', 'aborted', 'i/o')
                observations = (observed.diagnosis, *observed.evidence)
                hints = []
                for line in observations:
                    lower = line.casefold()
                    if lower.lstrip().startswith(('source:', 'limit:', 'where the messages', 'groups:')):
                        continue
                    if not any(signal in lower for signal in signals):
                        continue
                    for hint in item.evidence_hints:
                        if _clue_present(line[:10000], hint):
                            hints.append(hint)
                if hints:
                    matching.append(pair)
                    specificity += max(len(hint.split()) * 4 + min(len(hint), 25) / 10 for hint in hints)
            if matching:
                rank = (int(key in matching) * 100 + specificity
                    + int(item.category == result.category_key) * 10
                    + int(bool(item.checks) and item.checks[0] == key) * 24)
                possibilities.append((rank, item, matching))
        if not possibilities:
            return None
        possibilities.sort(key=lambda entry: (-entry[0], entry[1].id))
        _score, item, matching = possibilities[0]
        return AutomaticGuidance(item.title, item.possible_cause, item.steps, item.sources, tuple(dict.fromkeys(matching)), item.id)


    def plan(self, problem: str, ready_checks, *, max_checks: int = 13) -> InvestigationPlan:
        matches = self.knowledge.search(problem, limit=5)
        chosen = set()
        for match in matches[:3]:
            for pair in match.item.checks:
                if pair in ready_checks:
                    chosen.add(pair)
        skipped = tuple(sorted(chosen & NETWORK_OPT_IN_CHECKS))
        chosen -= NETWORK_OPT_IN_CHECKS
        # Prefer the top hypothesis and use catalogue order for repeatability.
        priority = [pair for m in matches[:3] for pair in m.item.checks if pair in chosen]
        ordered = list(dict.fromkeys(priority))[:max_checks]
        return InvestigationPlan(problem.strip()[:512], matches, tuple(ordered), skipped)

    def assess(self, plan: InvestigationPlan,
               results: Mapping[tuple[str, str], DiagnosticResult]) -> tuple[str, str, str]:
        """Return diagnosis, conditional guidance, and cited sources as text.

        Never call a proposed cause confirmed from symptom-text matching alone.
        Only positive warning/problem results within a case's check set may
        support a specific lead, and their observed text must match an expected
        clue. Even that remains a likely explanation pending user retest.
        """
        if not plan.matches:
            return ("No matching known problem was found in the offline knowledge base.\n"
                    "Try a more specific symptom or use Complete system scan.",
                    "Describe exactly what does not work and when it happens. "
                    "You can also select manual checks to gather more evidence.", "")
        examined = sum(pair in results for pair in plan.checks)
        leads: list[tuple[FoundItem,list[tuple[tuple[str,str],DiagnosticResult]]]] = []
        unsupported: list[FoundItem] = []
        for match in plan.matches[:3]:
            evidence = []
            for pair in match.item.checks:
                r = results.get(pair)
                if r is None or r.status not in (ResultStatus.WARNING, ResultStatus.PROBLEM):
                    continue
                raw = ' '.join([r.diagnosis, r.explanation, *r.evidence]).casefold()
                if any(hint.casefold() in raw for hint in match.item.evidence_hints if hint.strip()):
                    evidence.append((pair,r))
            if evidence:
                leads.append((match,evidence))
            else:
                unsupported.append(match)
        diagnosis = [f'Your problem: {plan.question}',
                     f'Checked: {examined} of {len(plan.checks)} planned local checks.', '']
        solutions = []
        if leads:
            diagnosis.append('What the measurements suggest (not a guaranteed root cause):')
            for num,(match, items) in enumerate(leads[:3],1):
                names=', '.join(f'{cat} / {check}' for (cat,check), _ in items)
                diagnosis.append(f'{num}. {match.item.title}\n   Possible explanation: {match.item.possible_cause}\n   Supporting checks: {names}')
                solutions.append(f'{num}. If this problem matches what you are experiencing — {match.item.title}:')
                solutions.extend('   - '+step for step in match.item.steps)
                solutions.append('   - After you make a change yourself, repeat the affected check to verify it.\n')
        else:
            diagnosis.append('No specific cause has been confirmed by these readings.')
            diagnosis.append('That does not mean the problem is imaginary or that the computer is healthy.')
            diagnosis.append('The following are possible explanations to investigate:')
            for num, match in enumerate(unsupported[:3],1):
                diagnosis.append(f'{num}. {match.item.title}: {match.item.possible_cause}')
            solutions.append('What you can investigate safely next:')
            # Offer conditional steps but never frame them as an existing fault.
            for num, match in enumerate(unsupported[:2],1):
                solutions.append(f'{num}. To investigate {match.item.title.lower()}:')
                solutions.extend('   - '+step for step in match.item.steps[:3])
        incomplete = [(pair, results[pair].status.value) for pair in plan.checks
                      if pair in results and results[pair].status in (ResultStatus.UNKNOWN, ResultStatus.NOT_RUN)]
        if incomplete:
            diagnosis.append('\nChecks that could not establish a result:')
            diagnosis.extend(f'- {cat} / {chk}: {status}' for (cat,chk),status in incomplete)
            solutions.append('Read Evidence / Logs for these checks before choosing a fix.')
        if examined < len(plan.checks):
            solutions.append('Some planned checks did not finish. Review their status before drawing conclusions.')
        urls = sorted(set(url for match in plan.matches[:3] for url in match.item.sources))
        refs = 'Original reference links for checking the general troubleshooting methods (not proof of a specific fault):\n' + '\n'.join(urls)
        return '\n'.join(diagnosis), '\n'.join(solutions), refs


@dataclass(frozen=True)
class AutomaticGuidance:
    """One evidence-linked knowledge-base suggestion, never a proven repair."""
    issue: str
    explanation: str
    steps: tuple[str, ...]
    sources: tuple[str, ...]
    supporting_checks: tuple[tuple[str, str], ...]
    case_id: str = ""

    @property
    def supporting_names(self) -> tuple[str, ...]:
        return tuple(_readable_check_name(pair) for pair in self.supporting_checks)


def _clue_present(text: str, hint: str) -> bool:
    """Match a bounded, whole phrase; ignore a clearly negated observation.

    Read-only check reports contain both errors and statements about absent
    errors. Looking for a substring blindly would turn 'no crash was found'
    into evidence of a crash.
    """
    needle = hint.casefold().strip()
    if len(needle) < 4:
        return False
    pattern = r'(?<!\w)' + re.escape(needle).replace(r'\ ', r'\s+') + r'(?!\w)'
    for match in re.finditer(pattern, text.casefold()):
        before = text[max(0, match.start() - 26):match.start()].casefold()
        if re.search(r'\b(?:no|without|not|never|zero|none|absent|cannot read|could not read)\s+(?:\w+\s+){0,3}$', before):
            continue
        return True
    return False


def _readable_check_name(pair: tuple[str, str]) -> str:
    for category in CATEGORIES:
        if category.key == pair[0]:
            for check in category.checks:
                if check.key == pair[1]:
                    return f'{category.title} / {check.title}'
    return ' / '.join(pair)


def _load_items_for_engine(engine: TroubleshootingEngine) -> dict[tuple[str, str], tuple[KnowledgeItem, ...]]:
    if not hasattr(engine, '_by_check'):
        mapping: dict[tuple[str, str], list[KnowledgeItem]] = {}
        with engine.knowledge._open() as con:
            rows = con.execute('SELECT * FROM problems ORDER BY id').fetchall()
        for row in rows:
            item = engine.knowledge._item(row)
            for pair in item.checks:
                mapping.setdefault(pair, []).append(item)
        engine._by_check = {key: tuple(items) for key, items in mapping.items()}
    return engine._by_check




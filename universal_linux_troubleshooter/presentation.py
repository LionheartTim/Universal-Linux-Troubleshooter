"""Truthful, copy-friendly result wording independent of the Qt GUI."""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Mapping
from .results import DiagnosticResult, ResultStatus
from .diagnostics.cause_analysis import analyze_cause, what_to_check_next
from .diagnostics.correlation import correlate_graphics_app_crash


_HEADINGS = {
    ResultStatus.OK: "Nothing unusual found in this check",
    ResultStatus.WARNING: "Something needs a closer look",
    ResultStatus.PROBLEM: "A problem was found in this check",
    ResultStatus.UNKNOWN: "Could not finish this check",
    ResultStatus.INFO: "Information from this check",
    ResultStatus.NOT_RUN: "This optional check was not started",
}

_SCOPE = {
    ResultStatus.PROBLEM: "Read the details before deciding what to change. This program never makes repairs for you.",
    ResultStatus.UNKNOWN: "The information available to this check is insufficient for a reliable result.",
    ResultStatus.INFO: "This is information, not a detected fault. You do not have to change anything just because of this result.",
    ResultStatus.NOT_RUN: "You chose not to run this optional test. Nothing was tested or sent online.",
}




@lru_cache(maxsize=1)
def _shared_knowledge_engine():
    # Created only when a real result needs to be interpreted. Cached so a
    # complete system scan does not reopen and re-index SQLite 30 times.
    from .knowledge import TroubleshootingEngine
    return TroubleshootingEngine()


def _knowledge_for(result, context=None):
    """Only add a useful, evidence-linked case, never a generic log-count article."""
    lead = _shared_knowledge_engine().automatic_guidance(result, context)
    if lead is None:
        return None
    # A generic journal topic does not explain any particular system failure.
    if lead.issue.casefold() in {"many red errors in system journal", "system errors", "general troubleshooting"}:
        return None
    # Check that the case actually offers a directed action, not just a
    # request for the user to read logs or look up a fix elsewhere.
    generic = ("evidence / logs", "compare the timestamp", "search for", "read the logs",
               "group messages", "match the message", "find out", "read the error")
    meaningful = [step for step in lead.steps if not any(term in step.casefold() for term in generic)]
    if not meaningful:
        return None
    return lead


def _knowledge_diagnosis(result, context=None):
    lead = _knowledge_for(result, context)
    if lead is None:
        return ''
    checks = ', '.join(lead.supporting_names)
    return ("Related finding:\n"
            f"{lead.issue}\n"
            f"Possible reason: {lead.explanation}\n"
            f"Supported by: {checks}")


def _knowledge_solution(result, context=None):
    lead = _knowledge_for(result, context)
    if lead is None:
        return ''
    useful = [step for step in lead.steps if not step.casefold().startswith(
        ("read evidence / logs", "group messages", "match the message"))]
    if not useful:
        return ''
    steps = '\n'.join(f'{number}. {step}' for number, step in enumerate(useful, 1))
    # Fetch alternate routes ONLY for an evidence-linked supported case.
    # Never present all database rows as if they were confirmed fixes.
    route_sections = []
    try:
        base = _shared_knowledge_engine()
        routes = base.knowledge.solution_routes(lead.case_id) if lead.case_id else ()
    except Exception:
        routes = ()
    for route in routes[:3]:
        route_sections.append('Option — ' + route.title + '\nWhen: ' + route.when_to_use +
            '\n' + '\n'.join(f'{i}. {step}' for i,step in enumerate(route.steps,1)) +
            '\nHow to check: ' + route.verification + '\nSafety: ' + route.safety)
    # Original citations remain in the local database for provenance; they
    # should not substitute for solutions in the beginner-facing UI.
    if route_sections:
        return (f"Alternative manual solutions for {lead.issue} (choose ONE matching your situation):\n" +
                "\n\n".join(route_sections) +
                "\nEach option is conditional, not a guaranteed fix. After making a change yourself, run the relevant check again to confirm its result. The program never applies changes.")
    return (f"Related guidance for {lead.issue}:\n{steps}\n"
            "After making a change yourself, run the relevant check again to confirm the result.")


def diagnosis_heading(result: DiagnosticResult) -> str:
    return _HEADINGS[result.status]


def diagnosis_body(result: DiagnosticResult, context: Mapping | None = None, *, include_cross_link: bool = True) -> str:
    message = f"What was found:\n{result.diagnosis}\n\nWhat this means:\n{result.explanation}"
    linked = _knowledge_diagnosis(result, context)
    if (result.category_key, result.check_key) == ("system", "system_logs") and "Cause and effect by area:" in result.explanation:
        # Append a cross-check only when two time-stamped records support it.
        link = _connection_diagnosis(context) if include_cross_link else ""
        return message + ("\n\n" + link if link else "")
    if result.status in (ResultStatus.WARNING, ResultStatus.PROBLEM, ResultStatus.UNKNOWN):
        # Keep the evidence-backed built-in cause explanation when available.
        # If an additional knowledge-base clue is supported, do not first
        # print a contradictory generic 'cause not confirmed' paragraph.
        if linked and analyze_cause(result) is None:
            message += "\n\nFinding the cause:\n" + linked
        else:
            message += "\n\nFinding the cause:\n" + what_to_check_next(result)
            if linked:
                message += "\n\nRelated knowledge-base information:\n" + linked
    elif result.status in _SCOPE:
        message += f"\n\nWhat this status means:\n{_SCOPE[result.status]}"
    return message


def _connection_diagnosis(context):
    if not context:
        return ''
    connection = correlate_graphics_app_crash(context)
    return ('Possible connection between two checks:\n' + connection.diagnosis) if connection else ''


def _connection_solution(context):
    if not context:
        return ''
    connection = correlate_graphics_app_crash(context)
    return ('Related crash and graphics error — suggested manual tests:\n' + connection.solution) if connection else ''


def solution_heading(result: DiagnosticResult) -> str:
    if result.status == ResultStatus.OK:
        return "No repair needed based on this check"
    if result.status == ResultStatus.UNKNOWN:
        return "What to try next · cause not known yet"
    if result.status == ResultStatus.INFO:
        return "What this information means"
    if result.status == ResultStatus.NOT_RUN:
        return "You can run this later"
    return "What you can do next"


def solution_body(result: DiagnosticResult, context: Mapping | None = None, *, include_cross_link: bool = True) -> str:
    if (result.category_key, result.check_key) == ("system", "system_logs") and "Suggested solutions based on the actual messages" in result.solution:
        link = _connection_solution(context) if include_cross_link else ""
        return (link + "\n\n" if link else "") + result.solution
    finding = analyze_cause(result)
    if finding is not None:
        primary = ("Why this may be happening:\n" + finding.connection +
                   "\n\nSteps you can take yourself:\n" + finding.next_steps +
                   "\n\nWhat the original check recommends:\n" + result.solution)
    else:
        primary = result.solution
    # Log and crash checks have their own concrete, evidence-derived guidance.
    # Do not dilute it with broad general-interest knowledge-base matches.
    if (result.category_key, result.check_key) in {
        ("system", "system_logs"), ("applications", "app_crashes")
    }:
        link = _connection_solution(context) if include_cross_link and result.check_key == "app_crashes" else ""
        return (link + "\n\n" if link else "") + primary
    linked = _knowledge_solution(result, context)
    return primary + ("\n\n" + linked if linked else "")


def evidence_body(result: DiagnosticResult) -> str:
    return "\n".join(result.evidence) if result.evidence else "No evidence recorded for this result."


def batch_summary(checks: tuple[tuple[str, str], ...], results: dict[tuple[str, str], DiagnosticResult], running=False) -> str:
    if not checks:
        return "Choose a check to see what happened."
    done = [results[key] for key in checks if key in results]
    counts = Counter(res.status for res in done)
    stat_parts = [f"{counts[status]} {name}" for status, name in (
        (ResultStatus.PROBLEM, "problem"), (ResultStatus.WARNING, "warning"),
        (ResultStatus.UNKNOWN, "unknown"), (ResultStatus.INFO, "info"),
        (ResultStatus.NOT_RUN, "not run"), (ResultStatus.OK, "OK"),
    ) if counts[status]]
    overview = f"{len(done)} of {len(checks)} checks complete"
    if stat_parts:
        overview += " · " + ", ".join(stat_parts)
    if len(done) == len(checks) and len(done) > 0 and counts[ResultStatus.OK] == len(done):
        overview += " · No issues found within the tested scope"
    elif not running and len(done) < len(checks):
        overview += " · Some checks have no result"
    return overview


def prioritize_check_results(checks, results):
    """Put problems and incomplete checks first without hiding any result."""
    order = {
        ResultStatus.PROBLEM: 0, ResultStatus.WARNING: 1,
        ResultStatus.UNKNOWN: 2, ResultStatus.INFO: 3,
        ResultStatus.NOT_RUN: 4, ResultStatus.OK: 5,
    }
    # Stable sort preserves catalogue order within each status.
    return tuple(sorted(checks, key=lambda key: order.get(
        results[key].status, 2) if key in results else -1))


def complete_scan_at_a_glance(checks, results):
    """Short, accurate beginner-oriented summary for the complete scan."""
    done = [results[k] for k in checks if k in results]
    counts = Counter(r.status for r in done)
    lines = [f"{len(done)} of {len(checks)} checks finished."]
    if counts[ResultStatus.PROBLEM]:
        lines.append(f"{counts[ResultStatus.PROBLEM]} check(s) found a problem that needs attention.")
    if counts[ResultStatus.WARNING]:
        lines.append(f"{counts[ResultStatus.WARNING]} check(s) found something worth investigating.")
    if counts[ResultStatus.UNKNOWN]:
        lines.append(f"{counts[ResultStatus.UNKNOWN]} check(s) could not get enough information.")
    if counts[ResultStatus.INFO]:
        lines.append(f"{counts[ResultStatus.INFO]} check(s) collected information only.")
    if counts[ResultStatus.OK]:
        lines.append(f"{counts[ResultStatus.OK]} check(s) found no problem in what they tested.")
    if counts[ResultStatus.NOT_RUN]:
        lines.append(f"{counts[ResultStatus.NOT_RUN]} optional check(s) were not run.")
    if not done:
        lines.append("No results have been collected yet.")
    elif len(done) < len(checks):
        lines.append("Some checks are still running or were stopped.")
    elif not (counts[ResultStatus.PROBLEM] or counts[ResultStatus.WARNING] or counts[ResultStatus.UNKNOWN]):
        lines.append("No problems were identified by the checks that could be completed.")
    lines.append("The Solution tab lists recommended actions first. Evidence / Logs contains the original technical details.")
    return "\n".join(lines)


def combined_check_view(checks, results, categories, *, include_categories=False):
    """Show every result, but put relevant repair plans first on Solution.

    OK and informational checks are kept in Diagnosis and Evidence/Logs and
    counted in Solution instead of drowning actual guidance in boilerplate.
    """
    labels = {(cat.key, chk.key):
              (f"{cat.title} > {chk.title}" if include_categories else chk.title)
              for cat in categories for chk in cat.checks}
    info, diagnosis, solutions, logs = [], [], [], []
    context = {pair: results[pair] for pair in checks if pair in results}
    resolved = []
    unavailable = []
    for index, pair in enumerate(checks, 1):
        title = labels.get(pair, pair[1])
        prefix = f"{index}. {title}"
        result = results.get(pair)
        info.append(f"{prefix}\nStatus: {'Not finished' if result is None else result.status.value}")
        if result is None:
            diagnosis.append(f"{prefix}\nNot finished yet. No result is available.")
            unavailable.append(title)
            logs.append(f"{prefix}\nNo information collected yet.")
            continue
        diagnosis.append(f"{prefix} — {result.status.value}\n{diagnosis_body(result, context, include_cross_link=False)}")
        logs.append(f"{prefix} — {result.status.value}\n{evidence_body(result)}")
        if result.status in (ResultStatus.PROBLEM, ResultStatus.WARNING, ResultStatus.UNKNOWN):
            solutions.append(f"{len(solutions) + 1}. {title} — {result.status.value}\n"
                             f"{solution_body(result, context, include_cross_link=False)}")
        else:
            resolved.append(result)
    connection = correlate_graphics_app_crash(context)
    if connection:
        diagnosis.insert(0, "Possible connection across two checks\n" + connection.diagnosis)
        logs.insert(0, "Cross-check evidence (original records):\n" + connection.evidence)
    action_view = ["Recommended steps for the findings that need attention"]
    if connection:
        action_view.append("Related graphics and application crash\n" + connection.solution)
    if solutions:
        action_view.extend(solutions)
    else:
        action_view.append("No repair actions were identified by the completed checks.")
    if resolved:
        complete_names = [labels.get((r.category_key, r.check_key), r.check_key)
                          for r in resolved]
        action_view.append(f"{len(resolved)} check(s) reported OK, Info or Not run; "
                           "no repair is suggested from those results: "
                           + ", ".join(complete_names) + ". "
                           "Details remain available in Diagnosis and Evidence / Logs.")
    if unavailable:
        action_view.append("Not completed: " + ", ".join(unavailable))
    return ("\n\n".join(info), "\n\n".join(diagnosis),
            "\n\n".join(action_view), "\n\n".join(logs))

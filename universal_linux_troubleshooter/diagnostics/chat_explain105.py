"""Beginner-friendly, verified documentary help for the AI conversation.

No shell execution, network requests, permission escalation or GUI navigation
is performed here. The commands are user-run references only. Do not present
internal check labels as instructions without explaining how to use them.
"""
from __future__ import annotations

import re

from .manual_cases40 import case_catalog


_CHECK_EXPLANATIONS = {
    'website name check': (
        '"Website name check" means checking DNS: can Linux find an IP address for a website name?',
        'Open your usual **host terminal** (not a terminal inside a container). Type:',
        'getent ahosts www.mozilla.org',
        'If you see one or more numbered IP addresses, name lookup worked at that moment. '
        'If you see no address or an error, DNS or connectivity may need further investigation. '
        'A successful lookup does **not** prove the website opens in your browser.',
        'This command is **run only by you**. It may contact your configured DNS resolver '
        'and reveal the looked-up domain to that service; it does not open the website.',
        'Does the command show any IP addresses, or an error?'
    ),
    'local gateway': (
        '"Local gateway" means checking which router Linux is configured to use; '
        'it does not test whether the router responds.',
        'Open your usual **host terminal** and type:',
        'ip -4 route show default',
        'A line beginning with `default via` usually shows the next-hop router address '
        'and interface. No line can be normal on an isolated network, or can indicate '
        'a missing default route. This alone does not prove the router is defective.',
        'This command only reads local routing settings. It does not contact the router '
        'or change your network.',
        'Do you see a `default via` line?'
    ),
    'ip configuration': (
        '"IP configuration" checks whether Linux has assigned a network address '
        'and a route for your connection. It does not test internet access.',
        'Open your usual **host terminal** and type:',
        'ip -br address',
        'Look for an `inet` address on the connection you are actually using. '
        'A missing address on an unused interface is not a problem by itself.',
        'This command reads only local network settings; it does not change anything.',
        'Is there an `inet` address on your active connection?'
    ),
    'wi-fi connection': (
        '"Wi-Fi connection" checks whether your Wi-Fi device reports an active '
        'connection. It cannot prove the internet works or measure past dropouts.',
        'If your computer uses NetworkManager, open a **host terminal** and type:',
        'nmcli device status',
        'Find the row for your Wi-Fi device. `connected` means NetworkManager '
        'reports a connection; `disconnected` does not mean the device is broken. '
        'On systems without NetworkManager, this command may not exist.',
        'The command reads local connection status; it does not reconnect or change settings.',
        'Does the Wi-Fi device show `connected`, `disconnected`, or is the command unavailable?'
    ),
}


def explain_named_check(message: str) -> str | None:
    """Explain a named check on an explicit request; never infer it ran."""
    text = ' '.join(message.casefold().split())
    if len(text) > 420:
        return None
    question = bool(re.search(r'\b(?:what|how|where|why|explain|run|find|open|use|mean|command|terminal|do i|can i)\b', text)) or text.endswith('?')
    if not question:
        return None
    for name, (meaning, instruction, command, interpretation, safety, followup) in _CHECK_EXPLANATIONS.items():
        if name in text or (name == 'website name check' and re.search(r'\b(?:dns lookup|dns test|name lookup)\b', text)):
            return ('**What this test checks**\n\n' + meaning + '\n\n'
                    '**How to run it**\n\n' + instruction + '\n\n'
                    '**COMMAND — run this yourself**\n\n```bash\n' + command + '\n```\n\n'
                    '**What the result means**\n\n' + interpretation + '\n\n'
                    '**Privacy and safety**\n\n' + safety + '\n\n'
                    '**Next question**\n\n' + followup)
    return None


def is_terminal_help_request(message: str) -> bool:
    """Only provide case commands when user explicitly asks for terminal help."""
    text = ' '.join(message.casefold().split())
    return (len(text) <= 420 and bool(re.search(
        r'\b(?:terminal|commands?|shell|cli|bash|console|command.line)\b', text))
        and bool(re.search(
        r'\b(?:show|give|list|which|how|what|run|use|try|help|steps|can|could|please|need|commands?)\b', text)))


def documented_terminal_help(message: str, case_id: str | None) -> str | None:
    """Show genuine documented *read-only* references for the current topic.

    Commands are sourced verbatim from 250-case tree; no repairs or arbitrary
    model-produced commands are authorised. Caller keeps the existing topic.
    """
    if not case_id or not is_terminal_help_request(message):
        return None
    case = case_catalog().get(case_id)
    if not case:
        return None
    references = case.get('terminal_result_guides', ())
    if not references:
        return ('There is no reviewed terminal command for this exact problem. '
                'I will not invent one. Manual Diagnostics can still run safe local checks.')
    lines = [f'**Terminal checks for: {case.get("title", "your problem")}**', '',
             'These are optional commands **you run yourself** in a host terminal. '
             'They are not executed by the Troubleshooter. Only use commands relevant '
             'to your situation; do not paste example placeholders literally.']
    for index, entry in enumerate(references, 1):
        command = entry.get('command', '')
        if not isinstance(command, str) or not command.strip():
            continue
        lines.extend(['', f'**TEST {index} — {entry.get("purpose", "Inspect the system")}**', '',
                      '**COMMAND**', '', '```bash', command.strip(), '```', '',
                      '**What the result can show**', '', str(entry.get('interpretation', '')), '',
                      '**What it does not prove**', '', str(entry.get('cannot_prove', ''))])
        cautions = [p for p in entry.get('precautions', ()) if isinstance(p, str) and p.strip()]
        if cautions:
            lines.extend(['', '**Safety notes**', '', *(f'- {p}' for p in cautions)])
    lines += ['', 'When a command is missing on your Linux system, tell me its exact error '
              'rather than installing a tool or changing settings without checking. '
              'If you share output, remove usernames, network addresses and other private details.']
    return '\n'.join(lines)


def is_contextual_help(message: str) -> bool:
    """Clarifications are not a new problem even without explicit topic words."""
    text = ' '.join(message.casefold().split())
    if len(text) > 240:
        return False
    return bool(re.search(r'\b(?:how do i|how can i|where do i|where is|what is|what does|what do you mean|explain|which command|terminal commands|what command|show me how|what next|which terminal command)\b', text))

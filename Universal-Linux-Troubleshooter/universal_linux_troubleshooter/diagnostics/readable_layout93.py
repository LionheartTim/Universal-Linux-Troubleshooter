"""Readable, safe, English-only HTML for the Manual Diagnostics pages.

Only display formatting is applied. Every source string and terminal command is
HTML-escaped. Nothing in this module executes shell commands, changes evidence,
or alters the separate plain-text copy of the documentation.
"""
from __future__ import annotations

from html import escape
from urllib.parse import urlsplit
import re

_HEADING = re.compile(r'^(?:[A-Z][A-Z0-9 /;:,()—–-]{4,}|STEP \d+|CHECK \d+|PATH \d+.*)$')
_MAJOR = ('SELF-GUIDED', 'USER-RUN TERMINAL', 'POSSIBLE SOLUTIONS',
          'INVESTIGATION STEPS', 'ADDITIONAL DEVICE', 'AFTER EACH ACTION',
          'CURRENT ASSESSMENT', 'LOCAL CHECK RESULTS', 'DOCUMENTED POSSIBILITIES',
          'COMPLETE TROUBLESHOOTING', 'FULL DOCUMENTED', 'AUTOMATIC READ-ONLY CHECK',
          'WHAT IS CHECKED', 'POSSIBLE CAUSES', 'REPORTED PROBLEM', 'EVIDENCE-SUPPORTED',
          'SELF-GUIDED DIAGNOSTIC', 'HARDWARE AND MANUFACTURER',
          'APPLICATION / DISTRIBUTION', 'RELEVANT TECHNICAL',
          'IF THE RESULT', 'HOW TO INTERPRET', 'A CLOSER LOOK', 'BEFORE YOU START', 'WHAT TO TRY', 'WHAT THE RESULTS MEAN', 'STEP-BY-STEP')
_SUBHEADINGS = frozenset({
    'WHAT THE RESULT CAN SHOW', 'WHAT IT DOES NOT PROVE',
    'SAFETY NOTE', 'BEFORE TAKING ACTION', 'STEPS', 'LIMITATIONS',
    'VERIFY THE ORIGINAL PROBLEM', 'VERIFY AFTERWARD', 'CHECK THIS FIRST',
})


def html_for_manual93(value: str) -> str:
    """Separate tests, commands, interpretation and grouped safety notes.

    Use spacing on *rendered blocks* rather than relying on blank lines; QText
    does not necessarily preserve the latter. The original source is untouched
    for the application's Copy tab text action.
    """
    if not value:
        return ''
    lines = value.splitlines()
    blocks = ['<html><body style="line-height:1.5;">']
    i = 0
    while i < len(lines):
        current = lines[i].strip()
        i += 1
        if not current:
            continue

        if current == 'REFERENCE URL':
            while i < len(lines) and not lines[i].strip():
                i += 1
            url = lines[i].strip() if i < len(lines) else ''
            if url:
                i += 1
            try:
                parsed = urlsplit(url)
            except ValueError:
                parsed = urlsplit('')
            if (parsed.scheme == 'https' and parsed.hostname and
                    parsed.username is None and parsed.password is None and
                    not any(c in url for c in '<>\\"\'')):
                blocks.append('<p style="margin:10px 0 18px 0;">'
                              '<b>OFFICIAL DOCUMENTATION</b> — '
                              '<a href="' + escape(url, quote=True) + '">'
                              + escape(parsed.hostname) + '</a></p>')
            else:
                blocks.append('<p style="margin:8px 0 16px 0;">' + escape(url) + '</p>')
            continue

        if current == 'COMMAND':
            while i < len(lines) and not lines[i].strip():
                i += 1
            command = lines[i].strip() if i < len(lines) else ''
            if command:
                i += 1
            blocks.append('<p style="margin:14px 0 7px 0;"><b>COMMAND</b></p>')
            if command:
                blocks.append('<pre style="margin:0 0 20px 0; padding:11px; '
                              'background-color:#1d3048; color:#f1f6ff; '
                              'white-space:pre-wrap; font-family:monospace;">'
                              + escape(command) + '</pre>')
            continue

        # Combine consecutive precautions under one heading and a genuine list.
        # This also works with a single entry, and never loses a second warning.
        if current.startswith(('- ', '• ')):
            items = [current[2:].strip()]
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith(('- ', '• ')):
                    items.append(next_line[2:].strip())
                    i += 1
                elif not next_line and i + 1 < len(lines) and lines[i+1].strip().startswith(('- ', '• ')):
                    i += 1
                else:
                    break
            blocks.append('<ul style="margin:7px 0 18px 20px; padding-left:12px;">'
                          + ''.join('<li style="margin-bottom:6px;">' + escape(item) + '</li>'
                                    for item in items if item) + '</ul>')
            continue

        if current.startswith('TOPIC ') and ' — ' in current:
            blocks.append('<hr style="margin:26px 0 18px 0; color:#43566c;"/>')
            blocks.append('<p style="margin:0 0 16px 0; font-size:large;"><b>' + escape(current) + '</b></p>')
            continue
        if current == '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━':
            continue
        is_test = current.startswith(('MANUAL TEST ', 'TERMINAL TEST '))
        is_major = any(current.startswith(prefix) for prefix in _MAJOR)
        if is_test:
            blocks.append('<hr style="margin:25px 0 16px 0; color:#43566c;"/>')
            blocks.append('<p style="margin:0 0 14px 0;"><b>' + escape(current) + '</b></p>')
        elif is_major:
            blocks.append('<hr style="margin:25px 0 15px 0;"/>')
            blocks.append('<p style="margin:0 0 13px 0;"><b>' + escape(current) + '</b></p>')
        elif current in _SUBHEADINGS:
            blocks.append('<p style="margin:15px 0 9px 0;"><b>' + escape(current) + '</b></p>')
        elif _HEADING.fullmatch(current) or current.startswith(('PATH ', 'STEP ', 'CHECK ')):
            blocks.append('<p style="margin:17px 0 10px 0;"><b>' + escape(current) + '</b></p>')
        else:
            blocks.append('<p style="margin:5px 0 17px 0;">' + escape(current) + '</p>')
    blocks.append('</body></html>')
    return '\n'.join(blocks)

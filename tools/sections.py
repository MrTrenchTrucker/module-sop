"""Shared Markdown section extraction for the module-sop tools (one implementation, reused by build + verify)."""
import re


def section(text, heading, stop_heading=None):
    """Return the section starting at the line `heading` up to (not including) `stop_heading`, or to EOF.

    Heading lines match with trailing whitespace tolerated, and a heading
    on the first line needs no preceding newline — an editor trimming
    spaces must never fail a gate. Raises ValueError if a heading is
    missing, so a renamed section fails loudly instead of returning nothing.
    """
    want = heading.strip()
    lines = text.split('\n')
    offs = []
    pos = 0
    for line in lines:
        offs.append(pos)
        pos += len(line) + 1

    def find(tag):
        tag = tag.strip()
        for i, line in enumerate(lines):
            if line.rstrip() == tag:
                return i
        return None

    s = find(want)
    if s is None:
        raise ValueError(f'heading not found: {heading!r}')
    if stop_heading is None:
        end = len(text)
    else:
        e = find(stop_heading)
        if e is None:
            raise ValueError(f'stop heading not found: {stop_heading!r}')
        end = offs[e]
    return text[offs[s]:end].rstrip('\n') + '\n'


def sop_version(text):
    """Return the '**Version:** x.y.z' value of an SOP, or raise ValueError."""
    m = re.search(r'\*\*Version:\*\* ([0-9][0-9.]*)', text)
    if not m:
        raise ValueError('no **Version:** line')
    return m.group(1)

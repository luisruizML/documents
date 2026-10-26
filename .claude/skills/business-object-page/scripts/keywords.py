"""Keyword strategy: which words of a Definition are bold.

Bold marks the concept, not emphasis: a reader who skims only the bold words can rebuild what the object is for.
Rules (agreed with the author):

  * 2 to 4 bold phrases in the Definition of a Vault object, each of 1 to 4 words;
  * the phrases are, in this order of priority, a behaviour (the history default, "replaced when it changes", "carries no
    description", "not stored"), a qualifier that tells two tables apart (current / over time, default / exception, identity /
    ownership) and the subject the table is about (names, identity documents, life events ...);
  * never bold the opening "The table that", a name in backticks, an example after "such as", or a link;
  * the page Definition section carries 3 to 6 bold phrases (the object's name on first use, what it identifies, its identity
    rule), checked for form only.

`propose` writes the bold phrases for a plain Definition; `bold_phrases` reads them back; the validator checks the form.
"""
from __future__ import annotations

import re

OPENING = "The table that"
MAX_WORDS = 4
VAULT_RANGE = (2, 4)
SECTION_RANGE = (3, 6)

BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
CODE_RE = re.compile(r"`[^`]*`")

# Behaviours: always bold when present. The pattern names the exact wording the pages use; group 1 is what turns bold.
BEHAVIOUR = [
    r"(earlier (?:ones|values|shapes|periods) stay)",
    r"(replaced when it changes)",
    r"(carries no (?:description|name|street|coordinates|choice))",
    r"(not stored)",
    r"(only the current)",
]
# Qualifiers: bold only to tell two tables apart.
QUALIFIER = [
    r"(over time)",
    r"It is (the default|the exception)",
    r"which is (the default)",
    r"which is (the exception)",
    r"(not the identity table)",
]

def _mask(text: str) -> str:
    """The text with each backtick span replaced by same-length filler, so no pattern matches inside a name."""
    return CODE_RE.sub(lambda m: "\0" * len(m.group(0)), text)


def strip_bold(text: str) -> str:
    return text.replace("**", "")


def bold_phrases(text: str) -> list[str]:
    return [m.group(1) for m in BOLD_RE.finditer(text)]


def _find(masked: str, phrase: str, start: int) -> tuple[int, int] | None:
    m = re.search(r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])", masked[start:])
    return (start + m.start(), start + m.end()) if m else None


def _first(masked: str, patterns: list[str]) -> list[tuple[int, int]]:
    out = []
    for pat in patterns:
        m = re.search(pat, masked)
        if m:
            out.append(m.span(1))
    return out


def propose(text: str, subjects: list[str] = (), limit: int = VAULT_RANGE[1]) -> str:
    """`text` with the approved bold phrases. `subjects` are the phrases chosen for this row (see `bold_terms.py`); they
    come first, then the behaviours, then the qualifiers, up to `limit` phrases in all."""
    plain = strip_bold(text)
    masked = _mask(plain)
    start = len(OPENING) if plain.startswith(OPENING) else 0
    ranked: list[tuple[int, int]] = []
    for phrase in subjects:
        span = _find(masked, phrase, start)
        if span is None:
            raise ValueError(f"bold phrase not found in the text: {phrase!r}")
        ranked.append(span)
    ranked += [s for s in _first(masked, BEHAVIOUR) + _first(masked, QUALIFIER) if s[0] >= start]
    kept: list[tuple[int, int]] = []
    for s in ranked:
        if len(kept) == limit:
            break
        if any(s[0] < k[1] and k[0] < s[1] for k in kept):
            continue
        kept.append(s)
    kept.sort()
    out, last = [], 0
    for a, b in kept:
        out += [plain[last:a], "**", plain[a:b], "**"]
        last = b
    out.append(plain[last:])
    return "".join(out)


def check_bold(label: str, text: str, low: int, high: int) -> list[str]:
    """Form errors of the bold phrases in `text`; `label` names the Definition."""
    errs = []
    if text.count("**") % 2:
        return [f"bold: '{label}' has an unclosed ** marker"]
    phrases = bold_phrases(text)
    if not low <= len(phrases) <= high:
        errs.append(f"bold: '{label}' has {len(phrases)} bold phrase(s); use {low} to {high}")
    seen = set()
    for p in phrases:
        if len(p.split()) > MAX_WORDS:
            errs.append(f"bold: '{label}' bolds '{p}', which is longer than {MAX_WORDS} words")
        if "`" in p:
            errs.append(f"bold: '{label}' bolds a name in backticks; names are already code")
        if p in seen:
            errs.append(f"bold: '{label}' bolds '{p}' twice")
        seen.add(p)
    plain = strip_bold(text)
    if plain.startswith(OPENING) and text.startswith("**"):
        errs.append(f"bold: '{label}' bolds the opening '{OPENING}'")
    return errs

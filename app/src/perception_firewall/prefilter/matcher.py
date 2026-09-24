"""Deterministic phrase matching. Python standard library only.

Matching behavior:

1. Case-insensitive — ``re.IGNORECASE``.
2. Unicode-safe — Python 3 ``str`` regexes are Unicode-aware by default;
   ``\\b``/``\\w`` recognize Unicode letters, not just ASCII.
3. Whitespace-normalized — multi-word phrases join their tokens with
   ``\\s+`` rather than a literal single space, so irregular whitespace in
   the source transcript (double spaces, tabs, newlines) does not prevent
   a match.
4. Punctuation-tolerant — punctuation is never stripped from the input;
   ``\\b`` word-boundary assertions naturally treat punctuation as a
   non-word character, so "blocked." still matches the pattern "blocked".
5. Original text is never modified — matching reads ``segment.text``
   as-is; nothing here rewrites or normalizes the text that ends up in
   ``Evidence.evidence_text``.
6. Multi-word phrases are matched as a whole, not as independent words.
7. ``\\b`` boundaries at the start and end of each compiled phrase prevent
   substring false positives (e.g. "pin" does not match inside "spinach").

Known limitation: apostrophe style is not normalized. A pattern written
with a straight apostrophe (``don't``) will not match a transcript that
uses a curly apostrophe (``don't`` with U+2019). See prefilter/README.md.
"""

from __future__ import annotations

import re
from typing import Iterator, Mapping, NamedTuple, Sequence

from perception_firewall.domain.evidence import EvidenceCategory

CompiledPattern = tuple[EvidenceCategory, str, "re.Pattern[str]"]


class PatternMatch(NamedTuple):
    """One (category, matched configured phrase) pair found in a text."""

    category: EvidenceCategory
    pattern: str


def _compile_phrase(phrase: str) -> "re.Pattern[str]":
    tokens = phrase.split()
    if not tokens:
        raise ValueError("pattern phrase must not be empty")
    escaped_tokens = [re.escape(token) for token in tokens]
    body = r"\s+".join(escaped_tokens)
    return re.compile(rf"\b{body}\b", re.IGNORECASE)


def compile_patterns(
    patterns: Mapping[EvidenceCategory, Sequence[str]],
) -> tuple[CompiledPattern, ...]:
    """Precompile every (category, phrase) pattern once, up front.

    Compiling here (rather than per call) keeps repeated matching cheap
    and keeps ``RuleBasedEvidenceProvider`` stateless with respect to any
    given transcript — the compiled patterns depend only on the
    configuration, never on input.
    """
    compiled: list[CompiledPattern] = []
    for category, phrases in patterns.items():
        for phrase in phrases:
            compiled.append((category, phrase, _compile_phrase(phrase)))
    return tuple(compiled)


def find_matches(
    text: str, compiled_patterns: Sequence[CompiledPattern]
) -> Iterator[PatternMatch]:
    """Yield one ``PatternMatch`` per configured phrase found in ``text``.

    This is presence-only: each phrase is checked with a single
    ``search()``, not counted. A phrase that appears multiple times in
    ``text`` still yields exactly one match — this is what gives the
    prefilter its within-segment duplicate protection, without any
    separate deduplication step being required here.
    """
    for category, phrase, regex in compiled_patterns:
        if regex.search(text):
            yield PatternMatch(category=category, pattern=phrase)

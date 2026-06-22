"""Checks passwords against a local breach corpus and scores them against
NIST SP 800-63B (Digital Identity Guidelines, memorized secret requirements):

  - Minimum length of 8 characters (the standard sets 8 as the floor and
    recommends allowing up to 64; it deliberately does NOT mandate
    mixed-case/digit/symbol composition rules).
  - Verifiers SHALL compare prospective secrets against a list of known
    compromised/commonly-used values and reject matches.
  - Repetitive (e.g. "aaaa") and sequential (e.g. "1234", "abcd") characters
    should be flagged/blocked.
  - Context-specific words (service name, username) should be disallowed.

The breach corpus is a small, locally curated list of well-known
common/breached passwords (sample_data/breach_corpus.txt) -- this performs
an offline lookup only; it never makes a network call to a live breach API.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

MIN_LENGTH_NIST = 8
MAX_LENGTH_NIST = 64


def load_breach_corpus(path: str | Path) -> set[str]:
    return {
        line.strip().lower()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def has_repetitive_run(password: str, run_length: int = 4) -> bool:
    return bool(re.search(r"(.)\1{" + str(run_length - 1) + r",}", password))


def has_sequential_run(password: str, run_length: int = 4) -> bool:
    lowered = password.lower()
    sequences = ("abcdefghijklmnopqrstuvwxyz", "0123456789")
    for seq in sequences:
        for i in range(len(seq) - run_length + 1):
            chunk = seq[i : i + run_length]
            if chunk in lowered or chunk[::-1] in lowered:
                return True
    return False


def contains_context_word(password: str, context_words: list[str]) -> str | None:
    lowered = password.lower()
    for word in context_words:
        word = word.strip().lower()
        if word and len(word) >= 3 and word in lowered:
            return word
    return None


@dataclass
class ComplianceResult:
    password: str
    length_ok: bool
    not_breached: bool
    not_repetitive: bool
    not_sequential: bool
    no_context_word: bool
    compliant: bool
    violations: list[str] = field(default_factory=list)


def check_nist_800_63b(
    password: str,
    breach_corpus: set[str] | None = None,
    context_words: list[str] | None = None,
) -> ComplianceResult:
    breach_corpus = breach_corpus or set()
    context_words = context_words or []

    violations = []

    length_ok = MIN_LENGTH_NIST <= len(password) <= MAX_LENGTH_NIST
    if not length_ok:
        if len(password) < MIN_LENGTH_NIST:
            violations.append(f"Below NIST 800-63B minimum length of {MIN_LENGTH_NIST} characters.")
        else:
            violations.append(f"Exceeds the {MAX_LENGTH_NIST}-character maximum recommended by NIST 800-63B.")

    not_breached = password.lower() not in breach_corpus
    if not not_breached:
        violations.append("Matches a known compromised/commonly-used password (breach corpus).")

    not_repetitive = not has_repetitive_run(password)
    if not not_repetitive:
        violations.append("Contains a repetitive character run (e.g. 'aaaa').")

    not_sequential = not has_sequential_run(password)
    if not not_sequential:
        violations.append("Contains a sequential character run (e.g. '1234', 'abcd').")

    matched_context = contains_context_word(password, context_words)
    no_context_word = matched_context is None
    if not no_context_word:
        violations.append(f"Contains context-specific word '{matched_context}' (e.g. username/service name).")

    compliant = length_ok and not_breached and not_repetitive and not_sequential and no_context_word

    return ComplianceResult(
        password=password,
        length_ok=length_ok,
        not_breached=not_breached,
        not_repetitive=not_repetitive,
        not_sequential=not_sequential,
        no_context_word=no_context_word,
        compliant=compliant,
        violations=violations,
    )


def check_batch(
    passwords: list[str],
    breach_corpus: set[str] | None = None,
    context_words: list[str] | None = None,
) -> list[ComplianceResult]:
    return [check_nist_800_63b(pw, breach_corpus, context_words) for pw in passwords]

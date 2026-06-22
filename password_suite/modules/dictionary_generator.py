"""Custom wordlist generator with pattern-based seeds and mutation rules."""
from __future__ import annotations

import itertools
from pathlib import Path

LEET_MAP = {
    "a": ["a", "4", "@"],
    "e": ["e", "3"],
    "i": ["i", "1", "!"],
    "o": ["o", "0"],
    "s": ["s", "5", "$"],
    "t": ["t", "7"],
}

COMMON_SUFFIXES = ["", "1", "12", "123", "!", "2024", "2025", "2026", "01"]

KEYBOARD_PATTERNS = [
    "qwerty", "asdf", "zxcv", "qazwsx", "1qaz2wsx", "qwertyuiop",
]

COMMON_PASSWORDS = [
    "password", "123456", "12345678", "letmein", "admin", "welcome",
    "iloveyou", "monkey", "dragon", "football", "baseball", "trustno1",
]


def leet_variants(word: str, limit: int = 8) -> list[str]:
    """Generate a bounded number of leet-speak substitutions for a word."""
    options = [LEET_MAP.get(ch.lower(), [ch]) for ch in word]
    variants = set()
    for combo in itertools.islice(itertools.product(*options), limit):
        variants.add("".join(combo))
    return list(variants)


def case_variants(word: str) -> list[str]:
    return list({word.lower(), word.upper(), word.capitalize()})


def build_from_seeds(names: list[str], dobs: list[str]) -> set[str]:
    """Combine names + dates of birth (DDMMYYYY, YYYY, MMYY style fragments)."""
    out = set()
    for name in names:
        for case_word in case_variants(name):
            out.add(case_word)
            for dob in dobs:
                out.add(f"{case_word}{dob}")
                out.add(f"{dob}{case_word}")
            for suffix in COMMON_SUFFIXES:
                out.add(f"{case_word}{suffix}")
    return out


def apply_mutations(words: set[str]) -> set[str]:
    mutated = set(words)
    for word in list(words):
        mutated.update(leet_variants(word))
        for suffix in COMMON_SUFFIXES:
            mutated.add(f"{word}{suffix}")
    return mutated


def generate_wordlist(
    names: list[str] | None = None,
    dobs: list[str] | None = None,
    include_common: bool = True,
    include_keyboard_patterns: bool = True,
    apply_leet: bool = True,
) -> list[str]:
    words: set[str] = set()

    if names:
        words.update(build_from_seeds(names, dobs or []))

    if include_common:
        words.update(COMMON_PASSWORDS)

    if include_keyboard_patterns:
        words.update(KEYBOARD_PATTERNS)

    if apply_leet:
        words = apply_mutations(words)

    return sorted(w for w in words if w)


def save_wordlist(words: list[str], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.write_text("\n".join(words) + "\n", encoding="utf-8")
    return output_path

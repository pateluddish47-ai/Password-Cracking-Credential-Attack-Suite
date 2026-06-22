"""Password strength analysis: complexity, entropy, dictionary/pattern checks."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

COMMON_PASSWORDS_PATH_DEFAULT = None  # set by caller if a wordlist is available

KEYBOARD_SEQUENCES = ["qwerty", "asdf", "zxcv", "qazwsx", "123456", "098765"]


@dataclass
class StrengthResult:
    password: str
    length: int
    entropy_bits: float
    has_lower: bool
    has_upper: bool
    has_digit: bool
    has_symbol: bool
    is_common: bool
    has_keyboard_pattern: bool
    severity: str
    recommendations: list[str] = field(default_factory=list)


def _charset_size(password: str) -> int:
    size = 0
    if re.search(r"[a-z]", password):
        size += 26
    if re.search(r"[A-Z]", password):
        size += 26
    if re.search(r"[0-9]", password):
        size += 10
    if re.search(r"[^a-zA-Z0-9]", password):
        size += 33
    return size or 1


def estimate_entropy(password: str) -> float:
    charset = _charset_size(password)
    return len(password) * math.log2(charset)


def detect_keyboard_pattern(password: str) -> bool:
    lowered = password.lower()
    return any(seq in lowered for seq in KEYBOARD_SEQUENCES)


def analyze_password(password: str, common_wordlist: set[str] | None = None) -> StrengthResult:
    common_wordlist = common_wordlist or set()
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_symbol = bool(re.search(r"[^a-zA-Z0-9]", password))
    is_common = password.lower() in common_wordlist
    has_pattern = detect_keyboard_pattern(password)
    entropy = estimate_entropy(password)

    recommendations = []
    if len(password) < 12:
        recommendations.append("Increase length to at least 12 characters.")
    if not has_upper:
        recommendations.append("Add uppercase letters.")
    if not has_lower:
        recommendations.append("Add lowercase letters.")
    if not has_digit:
        recommendations.append("Add digits.")
    if not has_symbol:
        recommendations.append("Add symbols/special characters.")
    if is_common:
        recommendations.append("Avoid common/dictionary passwords.")
    if has_pattern:
        recommendations.append("Avoid keyboard-walk patterns (e.g. qwerty, 12345).")

    if is_common or entropy < 28:
        severity = "Critical"
    elif entropy < 40 or has_pattern:
        severity = "High"
    elif entropy < 60:
        severity = "Medium"
    else:
        severity = "Low"

    return StrengthResult(
        password=password,
        length=len(password),
        entropy_bits=round(entropy, 2),
        has_lower=has_lower,
        has_upper=has_upper,
        has_digit=has_digit,
        has_symbol=has_symbol,
        is_common=is_common,
        has_keyboard_pattern=has_pattern,
        severity=severity,
        recommendations=recommendations,
    )


def analyze_batch(passwords: list[str], common_wordlist: set[str] | None = None) -> list[StrengthResult]:
    return [analyze_password(pw, common_wordlist) for pw in passwords]

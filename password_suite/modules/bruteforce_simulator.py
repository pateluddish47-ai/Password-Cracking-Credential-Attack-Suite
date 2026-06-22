"""Dictionary-attack and incremental brute-force simulation against hashes
the user supplies from their own controlled lab. Brute-force mode only
actually enumerates small search spaces (demo purposes); for larger spaces it
reports a mathematically estimated time-to-crack instead of iterating, since
exhaustive enumeration of realistic keyspaces is not something a teaching
tool should attempt.
"""
from __future__ import annotations

import hashlib
import itertools
import string
import time
from dataclasses import dataclass, field

HASH_FUNCS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}

CHARSETS = {
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": "!@#$%^&*()-_=+",
}

# A conservative reference guesses-per-second rate for offline estimation
# (single consumer GPU on a slow, salted hash). Adjust per the algorithm
# being modeled when reporting estimates.
DEFAULT_GUESS_RATE = 1_000_000


def _hash_word(word: str, algorithm: str) -> str:
    func = HASH_FUNCS.get(algorithm.lower())
    if func is None:
        raise ValueError(f"Unsupported algorithm for simulation: {algorithm}")
    return func(word.encode("utf-8")).hexdigest()


@dataclass
class DictionaryAttackResult:
    target_hash: str
    algorithm: str
    cracked: bool
    matched_word: str | None
    attempts: int
    elapsed_seconds: float


def dictionary_attack(target_hash: str, wordlist: list[str], algorithm: str) -> DictionaryAttackResult:
    start = time.perf_counter()
    target_hash = target_hash.lower()
    for attempts, word in enumerate(wordlist, start=1):
        if _hash_word(word, algorithm) == target_hash:
            return DictionaryAttackResult(
                target_hash=target_hash,
                algorithm=algorithm,
                cracked=True,
                matched_word=word,
                attempts=attempts,
                elapsed_seconds=time.perf_counter() - start,
            )
    return DictionaryAttackResult(
        target_hash=target_hash,
        algorithm=algorithm,
        cracked=False,
        matched_word=None,
        attempts=len(wordlist),
        elapsed_seconds=time.perf_counter() - start,
    )


@dataclass
class BruteForceEstimate:
    charset_size: int
    min_length: int
    max_length: int
    keyspace_size: int
    guess_rate: int
    estimated_seconds: float
    estimated_human: str = field(default="")

    def __post_init__(self):
        self.estimated_human = format_duration(self.estimated_seconds)


def format_duration(seconds: float) -> str:
    units = [
        ("years", 365 * 24 * 3600),
        ("days", 24 * 3600),
        ("hours", 3600),
        ("minutes", 60),
        ("seconds", 1),
    ]
    if seconds < 1:
        return "<1 second"
    parts = []
    remaining = seconds
    for name, size in units:
        value = int(remaining // size)
        if value:
            parts.append(f"{value} {name}")
            remaining -= value * size
    return ", ".join(parts[:2]) if parts else "<1 second"


def estimate_bruteforce_time(
    charsets: list[str],
    min_length: int,
    max_length: int,
    guess_rate: int = DEFAULT_GUESS_RATE,
) -> BruteForceEstimate:
    pool = "".join(CHARSETS[name] for name in charsets if name in CHARSETS)
    charset_size = len(pool) or 1
    keyspace = sum(charset_size ** n for n in range(min_length, max_length + 1))
    estimated_seconds = keyspace / guess_rate
    return BruteForceEstimate(
        charset_size=charset_size,
        min_length=min_length,
        max_length=max_length,
        keyspace_size=keyspace,
        guess_rate=guess_rate,
        estimated_seconds=estimated_seconds,
    )


def incremental_bruteforce_demo(
    target_hash: str,
    algorithm: str,
    charsets: list[str],
    max_length: int = 4,
) -> DictionaryAttackResult:
    """Actually enumerates a small keyspace (max_length capped) as a teaching
    demo of incremental brute-force; not intended for real-world cracking.
    """
    pool = "".join(CHARSETS[name] for name in charsets if name in CHARSETS) or string.ascii_lowercase
    target_hash = target_hash.lower()
    start = time.perf_counter()
    attempts = 0
    for length in range(1, max_length + 1):
        for combo in itertools.product(pool, repeat=length):
            attempts += 1
            candidate = "".join(combo)
            if _hash_word(candidate, algorithm) == target_hash:
                return DictionaryAttackResult(
                    target_hash=target_hash,
                    algorithm=algorithm,
                    cracked=True,
                    matched_word=candidate,
                    attempts=attempts,
                    elapsed_seconds=time.perf_counter() - start,
                )
    return DictionaryAttackResult(
        target_hash=target_hash,
        algorithm=algorithm,
        cracked=False,
        matched_word=None,
        attempts=attempts,
        elapsed_seconds=time.perf_counter() - start,
    )

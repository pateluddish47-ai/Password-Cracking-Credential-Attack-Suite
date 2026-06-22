"""Verifies candidate passwords against real Linux crypt-style hashes
($1$ MD5, $5$ SHA-256, $6$ SHA-512, bcrypt) using passlib, instead of the
raw hashlib digests used by bruteforce_simulator. This is what makes a
dictionary attack against an actual /etc/shadow-style hash work end to end.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from passlib.hash import bcrypt, md5_crypt, sha256_crypt, sha512_crypt

SCHEME_MAP = {
    "MD5": md5_crypt,
    "SHA-256": sha256_crypt,
    "SHA-512": sha512_crypt,
    "Blowfish (bcrypt)": bcrypt,
}


def verify_crypt_password(candidate: str, hash_value: str, algorithm: str) -> bool:
    scheme = SCHEME_MAP.get(algorithm)
    if scheme is None:
        raise ValueError(f"Unsupported crypt algorithm for verification: {algorithm}")
    try:
        return scheme.verify(candidate, hash_value)
    except ValueError:
        return False


@dataclass
class CryptAttackResult:
    hash_value: str
    algorithm: str
    cracked: bool
    matched_word: str | None
    attempts: int
    elapsed_seconds: float


def dictionary_attack_crypt(hash_value: str, algorithm: str, wordlist: list[str]) -> CryptAttackResult:
    start = time.perf_counter()
    for attempts, word in enumerate(wordlist, start=1):
        if verify_crypt_password(word, hash_value, algorithm):
            return CryptAttackResult(
                hash_value=hash_value,
                algorithm=algorithm,
                cracked=True,
                matched_word=word,
                attempts=attempts,
                elapsed_seconds=time.perf_counter() - start,
            )
    return CryptAttackResult(
        hash_value=hash_value,
        algorithm=algorithm,
        cracked=False,
        matched_word=None,
        attempts=len(wordlist),
        elapsed_seconds=time.perf_counter() - start,
    )

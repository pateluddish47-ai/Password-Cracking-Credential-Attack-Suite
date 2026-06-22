"""Parses already-exported credential files (Linux shadow / Windows SAM dumps)
and identifies the hashing algorithm in use. This module does not access the
live filesystem or registry itself -- it only parses text that the user
supplies from their own controlled lab environment (e.g. a copy of
/etc/shadow, or the output of `samdump2`/`secretsdump.py` run by the user).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SHADOW_ALGO_IDS = {
    "1": "MD5",
    "2a": "Blowfish (bcrypt)",
    "5": "SHA-256",
    "6": "SHA-512",
    "y": "yescrypt",
}


@dataclass
class Credential:
    username: str
    hash_value: str
    algorithm: str
    source: str


def identify_shadow_algorithm(hash_field: str) -> str:
    if not hash_field or hash_field in ("*", "!", "!!"):
        return "locked/disabled account"
    if hash_field.startswith("$"):
        parts = hash_field.split("$")
        if len(parts) > 1 and parts[1] in SHADOW_ALGO_IDS:
            return SHADOW_ALGO_IDS[parts[1]]
        return "unknown $id$ format"
    return "DES (legacy crypt)"


def parse_shadow_file(path: str | Path) -> list[Credential]:
    """Parse a Linux /etc/shadow-formatted file: user:hash:lastchg:..."""
    creds = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(":")
        if len(fields) < 2:
            continue
        username, hash_field = fields[0], fields[1]
        algo = identify_shadow_algorithm(hash_field)
        creds.append(Credential(username, hash_field, algo, source="linux_shadow"))
    return creds


def parse_sam_dump(path: str | Path) -> list[Credential]:
    """Parse a SAM-style dump line: user:rid:LMHASH:NTHASH:::
    (as produced offline by tools such as samdump2 or secretsdump.py).
    """
    creds = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split(":")
        if len(fields) < 4:
            continue
        username, _rid, lm_hash, nt_hash = fields[0], fields[1], fields[2], fields[3]
        empty_lm = "aad3b435b51404eeaad3b435b51404ee"
        empty_nt = "31d6cfe0d16ae931b73c59d7e0c089c0"
        if nt_hash and nt_hash.lower() != empty_nt:
            creds.append(Credential(username, nt_hash, "NTLM", source="windows_sam"))
        if lm_hash and lm_hash.lower() != empty_lm:
            creds.append(Credential(username, lm_hash, "LM (legacy, weak)", source="windows_sam"))
    return creds

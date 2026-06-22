"""Benchmarks the actual hashing speed of the machine running the toolkit,
so brute-force time-to-crack estimates are based on a measured rate rather
than a guessed constant.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from .bruteforce_simulator import HASH_FUNCS
from .crypt_verifier import SCHEME_MAP


@dataclass
class BenchmarkResult:
    algorithm: str
    hashes_per_second: float
    sample_count: int
    elapsed_seconds: float


def benchmark_fast_hash(algorithm: str, duration: float = 1.0) -> BenchmarkResult:
    """Benchmark a fast, unsalted digest algorithm (md5/sha1/sha256/sha512)."""
    func = HASH_FUNCS.get(algorithm.lower())
    if func is None:
        raise ValueError(f"Unsupported algorithm for benchmarking: {algorithm}")

    count = 0
    start = time.perf_counter()
    while time.perf_counter() - start < duration:
        func(str(count).encode("utf-8")).hexdigest()
        count += 1
    elapsed = time.perf_counter() - start
    return BenchmarkResult(
        algorithm=algorithm,
        hashes_per_second=count / elapsed,
        sample_count=count,
        elapsed_seconds=elapsed,
    )


def benchmark_crypt_hash(algorithm: str, sample_size: int = 5) -> BenchmarkResult:
    """Benchmark a slow, salted crypt scheme (MD5/SHA-256/SHA-512 crypt, bcrypt).

    Crypt schemes are designed to be slow, so this measures verifications
    against a freshly generated hash rather than running for a fixed duration.
    """
    scheme = SCHEME_MAP.get(algorithm)
    if scheme is None:
        raise ValueError(f"Unsupported crypt algorithm for benchmarking: {algorithm}")

    reference_hash = scheme.hash("benchmark-reference-password")
    start = time.perf_counter()
    for _ in range(sample_size):
        scheme.verify("incorrect-guess", reference_hash)
    elapsed = time.perf_counter() - start
    return BenchmarkResult(
        algorithm=algorithm,
        hashes_per_second=sample_size / elapsed if elapsed > 0 else float("inf"),
        sample_count=sample_size,
        elapsed_seconds=elapsed,
    )

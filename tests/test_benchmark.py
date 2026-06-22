from modules import benchmark as bm


def test_benchmark_fast_hash_returns_positive_rate():
    result = bm.benchmark_fast_hash("sha256", duration=0.1)
    assert result.hashes_per_second > 0
    assert result.sample_count > 0


def test_benchmark_crypt_hash_returns_positive_rate():
    result = bm.benchmark_crypt_hash("MD5", sample_size=2)
    assert result.hashes_per_second > 0
    assert result.sample_count == 2

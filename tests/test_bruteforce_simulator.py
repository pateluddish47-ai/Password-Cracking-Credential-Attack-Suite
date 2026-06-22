import hashlib

from modules import bruteforce_simulator as bf


def test_dictionary_attack_finds_match():
    target = hashlib.sha256(b"letmein").hexdigest()
    result = bf.dictionary_attack(target, ["wrong", "letmein", "also-wrong"], "sha256")
    assert result.cracked
    assert result.matched_word == "letmein"
    assert result.attempts == 2


def test_dictionary_attack_no_match():
    target = hashlib.sha256(b"unguessable").hexdigest()
    result = bf.dictionary_attack(target, ["wrong", "also-wrong"], "sha256")
    assert not result.cracked
    assert result.matched_word is None


def test_estimate_bruteforce_time_keyspace_grows_with_length():
    short = bf.estimate_bruteforce_time(["lower"], 1, 2)
    long = bf.estimate_bruteforce_time(["lower"], 1, 4)
    assert long.keyspace_size > short.keyspace_size


def test_format_duration_human_readable():
    assert bf.format_duration(0.5) == "<1 second"
    assert "minute" in bf.format_duration(125)


def test_incremental_bruteforce_demo_cracks_small_keyspace():
    target = hashlib.md5(b"a1").hexdigest()
    result = bf.incremental_bruteforce_demo(target, "md5", ["lower", "digits"], max_length=2)
    assert result.cracked
    assert result.matched_word == "a1"

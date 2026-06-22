from modules import dictionary_generator as dg


def test_leet_variants_includes_original_word_and_same_length():
    variants = dg.leet_variants("pass")
    assert "pass" in variants
    assert all(len(v) == len("pass") for v in variants)


def test_case_variants_returns_three_forms():
    variants = dg.case_variants("alice")
    assert "alice" in variants
    assert "ALICE" in variants
    assert "Alice" in variants


def test_build_from_seeds_combines_name_and_dob():
    words = dg.build_from_seeds(["Alice"], ["1995"])
    assert any("1995" in w for w in words)
    assert any(w.lower().startswith("alice") for w in words)


def test_generate_wordlist_includes_common_passwords():
    words = dg.generate_wordlist(include_common=True, apply_leet=False)
    assert "password" in words


def test_generate_wordlist_excludes_common_when_disabled():
    words = dg.generate_wordlist(include_common=False, include_keyboard_patterns=False, apply_leet=False)
    assert "password" not in words


def test_save_wordlist_writes_file(tmp_path):
    out = dg.save_wordlist(["one", "two"], tmp_path / "wl.txt")
    assert out.read_text(encoding="utf-8").splitlines() == ["one", "two"]

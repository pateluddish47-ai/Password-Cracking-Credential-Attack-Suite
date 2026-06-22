from modules import compliance_checker as cc


def test_has_repetitive_run():
    assert cc.has_repetitive_run("aaaa1234")
    assert not cc.has_repetitive_run("abcdef12")


def test_has_sequential_run():
    assert cc.has_sequential_run("xy1234zz")
    assert cc.has_sequential_run("abcdxyz")
    assert not cc.has_sequential_run("Xk9mQ2vL")


def test_contains_context_word():
    assert cc.contains_context_word("alice2026!", ["alice"]) == "alice"
    assert cc.contains_context_word("Xk9mQ2vL", ["alice"]) is None


def test_check_nist_800_63b_flags_breached_password():
    result = cc.check_nist_800_63b("password123", breach_corpus={"password123"})
    assert not result.compliant
    assert not result.not_breached


def test_check_nist_800_63b_compliant_password():
    result = cc.check_nist_800_63b("Xk9$mQ2#vL8pR4z", breach_corpus=set())
    assert result.compliant


def test_check_nist_800_63b_too_short():
    result = cc.check_nist_800_63b("ab1!", breach_corpus=set())
    assert not result.length_ok
    assert not result.compliant


def test_check_batch_returns_one_result_per_password():
    results = cc.check_batch(["abc", "Xk9$mQ2#vL8pR4z"], breach_corpus=set())
    assert len(results) == 2

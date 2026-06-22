from modules import strength_analyzer as sa


def test_estimate_entropy_increases_with_charset_diversity():
    only_lower = sa.estimate_entropy("aaaaaaaa")
    mixed = sa.estimate_entropy("aA1!aA1!")
    assert mixed > only_lower


def test_detect_keyboard_pattern():
    assert sa.detect_keyboard_pattern("myqwertypass")
    assert not sa.detect_keyboard_pattern("Xk9mQ2vL8pR")


def test_analyze_password_flags_common_password():
    result = sa.analyze_password("password", common_wordlist={"password"})
    assert result.is_common
    assert result.severity == "Critical"


def test_analyze_password_strong_password_has_low_severity():
    result = sa.analyze_password("Xk9$mQ2#vL8pR4z")
    assert result.severity == "Low"
    assert not result.recommendations


def test_analyze_password_short_password_recommends_length():
    result = sa.analyze_password("ab1!")
    assert any("length" in rec.lower() for rec in result.recommendations)


def test_analyze_batch_returns_one_result_per_password():
    results = sa.analyze_batch(["abc", "Xk9$mQ2#vL8pR4z"])
    assert len(results) == 2

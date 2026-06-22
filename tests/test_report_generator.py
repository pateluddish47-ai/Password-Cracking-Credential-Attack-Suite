from modules import compliance_checker as cc
from modules import report_generator as rg
from modules import strength_analyzer as sa


def test_generate_report_includes_executive_summary():
    results = sa.analyze_batch(["password", "Xk9$mQ2#vL8pR4z"], common_wordlist={"password"})
    report = rg.generate_report(results)
    assert "Executive Summary" in report
    assert "password" in report


def test_generate_report_includes_compliance_section():
    results = sa.analyze_batch(["password"], common_wordlist={"password"})
    compliance = cc.check_batch(["password"], breach_corpus={"password"})
    report = rg.generate_report(results, compliance_results=compliance)
    assert "NIST SP 800-63B Compliance Check" in report
    assert "Compliant: 0/1" in report


def test_save_report_writes_file(tmp_path):
    out = rg.save_report("# Test Report", tmp_path / "report.md")
    assert out.read_text(encoding="utf-8") == "# Test Report"

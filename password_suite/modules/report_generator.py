"""Aggregates results from the other modules into a markdown audit report."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .bruteforce_simulator import BruteForceEstimate, DictionaryAttackResult
from .compliance_checker import ComplianceResult
from .strength_analyzer import StrengthResult


def _strength_table(results: list[StrengthResult]) -> str:
    lines = [
        "| Password | Length | Entropy (bits) | Severity | Common? | Keyboard Pattern? |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| `{r.password}` | {r.length} | {r.entropy_bits} | {r.severity} | "
            f"{'Yes' if r.is_common else 'No'} | {'Yes' if r.has_keyboard_pattern else 'No'} |"
        )
    return "\n".join(lines)


def _recommendations(results: list[StrengthResult]) -> str:
    seen: dict[str, None] = {}
    for r in results:
        for rec in r.recommendations:
            seen.setdefault(rec, None)
    if not seen:
        return "No additional recommendations -- passwords meet baseline policy."
    return "\n".join(f"- {rec}" for rec in seen)


def _compliance_table(results: list[ComplianceResult]) -> str:
    lines = [
        "| Password | NIST 800-63B Compliant? | Violations |",
        "|---|---|---|",
    ]
    for r in results:
        violation_text = "; ".join(r.violations) if r.violations else "None"
        lines.append(f"| `{r.password}` | {'Yes' if r.compliant else 'No'} | {violation_text} |")
    return "\n".join(lines)


def generate_report(
    strength_results: list[StrengthResult],
    dictionary_results: list[DictionaryAttackResult] | None = None,
    bruteforce_estimates: list[BruteForceEstimate] | None = None,
    compliance_results: list[ComplianceResult] | None = None,
    chart_paths: list[str] | None = None,
) -> str:
    dictionary_results = dictionary_results or []
    bruteforce_estimates = bruteforce_estimates or []
    compliance_results = compliance_results or []
    chart_paths = chart_paths or []

    severities = [r.severity for r in strength_results]
    summary_counts = {
        s: severities.count(s) for s in ("Critical", "High", "Medium", "Low")
    }

    report_lines = [
        "# Password Security Audit Report",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Executive Summary",
        f"- Passwords analyzed: {len(strength_results)}",
        f"- Critical: {summary_counts['Critical']}  |  High: {summary_counts['High']}  |  "
        f"Medium: {summary_counts['Medium']}  |  Low: {summary_counts['Low']}",
        "",
        "## Password Strength Analysis",
        _strength_table(strength_results) if strength_results else "_No passwords analyzed._",
        "",
        "## Dictionary Attack Simulation Results",
    ]

    if dictionary_results:
        report_lines.append("| Target Hash | Algorithm | Cracked? | Matched Word | Attempts | Time (s) |")
        report_lines.append("|---|---|---|---|---|---|")
        for d in dictionary_results:
            report_lines.append(
                f"| `{d.target_hash[:16]}...` | {d.algorithm} | {'Yes' if d.cracked else 'No'} | "
                f"{d.matched_word or '-'} | {d.attempts} | {d.elapsed_seconds:.4f} |"
            )
    else:
        report_lines.append("_No dictionary attack simulations run._")

    report_lines += ["", "## Brute-Force Time-to-Crack Estimates"]
    if bruteforce_estimates:
        report_lines.append("| Charset Size | Length Range | Keyspace | Guess Rate/s | Estimated Time |")
        report_lines.append("|---|---|---|---|---|")
        for b in bruteforce_estimates:
            report_lines.append(
                f"| {b.charset_size} | {b.min_length}-{b.max_length} | {b.keyspace_size:,} | "
                f"{b.guess_rate:,} | {b.estimated_human} |"
            )
    else:
        report_lines.append("_No brute-force estimates computed._")

    report_lines += ["", "## NIST SP 800-63B Compliance Check"]
    if compliance_results:
        compliant_count = sum(1 for r in compliance_results if r.compliant)
        report_lines.append(f"- Compliant: {compliant_count}/{len(compliance_results)}")
        report_lines.append("")
        report_lines.append(_compliance_table(compliance_results))
    else:
        report_lines.append("_No compliance checks run._")

    if chart_paths:
        report_lines += ["", "## Visual Analytics"]
        for path in chart_paths:
            report_lines.append(f"![chart]({path})")

    report_lines += [
        "",
        "## Recommendations",
        _recommendations(strength_results),
        "",
        "## Recommended Password Policy",
        "- Minimum length: 12 characters (14+ for privileged accounts).",
        "- Require a mix of uppercase, lowercase, digits, and symbols.",
        "- Block known-breached and common passwords (e.g. via Have I Been Pwned API or local blocklist).",
        "- Enforce account lockout / rate limiting after repeated failed attempts.",
        "- Use salted, slow hashing algorithms (bcrypt, scrypt, Argon2) for storage -- never unsalted MD5/SHA1.",
        "- Enable multi-factor authentication wherever possible.",
        "- Rotate credentials immediately if found in a breach dataset.",
    ]

    return "\n".join(report_lines)


def save_report(report_text: str, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.write_text(report_text, encoding="utf-8")
    return output_path

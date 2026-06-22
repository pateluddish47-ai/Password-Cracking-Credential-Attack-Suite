#!/usr/bin/env python3
"""Password Cracking & Credential Attack Suite -- CLI entrypoint.

Ethical, simulation-only toolkit for password policy auditing. Intended
for use only against test data / accounts you own or are authorized to
assess in a controlled lab environment.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from modules import (
    benchmark as bm,
    bruteforce_simulator as bf,
    compliance_checker as cc,
    crypt_verifier as cv,
    dictionary_generator as dg,
    hash_extractor as he,
    report_generator as rg,
    strength_analyzer as sa,
    visualizations as viz,
)


def cmd_gen_dict(args: argparse.Namespace) -> None:
    names = args.names.split(",") if args.names else []
    dobs = args.dobs.split(",") if args.dobs else []
    words = dg.generate_wordlist(
        names=names,
        dobs=dobs,
        include_common=not args.no_common,
        include_keyboard_patterns=not args.no_keyboard,
        apply_leet=not args.no_leet,
    )
    out = dg.save_wordlist(words, args.output)
    print(f"Generated {len(words)} candidate passwords -> {out}")


def cmd_extract_hashes(args: argparse.Namespace) -> None:
    if args.format == "shadow":
        creds = he.parse_shadow_file(args.input)
    else:
        creds = he.parse_sam_dump(args.input)

    if not creds:
        print("No credential entries parsed.")
        return

    for c in creds:
        print(f"[{c.source}] {c.username}: algorithm={c.algorithm} hash={c.hash_value[:32]}...")

    if args.output:
        lines = [f"{c.username}:{c.hash_value}:{c.algorithm}:{c.source}" for c in creds]
        Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Saved {len(creds)} entries -> {args.output}")


def cmd_dict_attack(args: argparse.Namespace) -> None:
    wordlist = Path(args.wordlist).read_text(encoding="utf-8").splitlines()
    result = bf.dictionary_attack(args.target_hash, wordlist, args.algorithm)
    status = "CRACKED" if result.cracked else "NOT CRACKED"
    print(f"{status} -- attempts={result.attempts} time={result.elapsed_seconds:.4f}s")
    if result.cracked:
        print(f"Matched password: {result.matched_word}")


def cmd_bruteforce_estimate(args: argparse.Namespace) -> None:
    charsets = args.charsets.split(",")
    guess_rate = args.guess_rate
    if args.benchmark_algorithm:
        bench = bm.benchmark_fast_hash(args.benchmark_algorithm, duration=args.benchmark_duration)
        guess_rate = int(bench.hashes_per_second)
        print(f"Live benchmark: {args.benchmark_algorithm} -> {guess_rate:,} hashes/sec on this machine")

    est = bf.estimate_bruteforce_time(charsets, args.min_length, args.max_length, guess_rate)
    print(f"Charset size: {est.charset_size}")
    print(f"Keyspace size: {est.keyspace_size:,}")
    print(f"Guess rate: {est.guess_rate:,}/s")
    print(f"Estimated time to exhaust keyspace: {est.estimated_human}")


def cmd_bruteforce_demo(args: argparse.Namespace) -> None:
    charsets = args.charsets.split(",")
    result = bf.incremental_bruteforce_demo(args.target_hash, args.algorithm, charsets, args.max_length)
    status = "CRACKED" if result.cracked else "NOT CRACKED"
    print(f"{status} -- attempts={result.attempts} time={result.elapsed_seconds:.4f}s")
    if result.cracked:
        print(f"Matched password: {result.matched_word}")


def cmd_analyze(args: argparse.Namespace) -> None:
    passwords = Path(args.input).read_text(encoding="utf-8").splitlines()
    passwords = [p for p in passwords if p.strip()]
    common = set(dg.COMMON_PASSWORDS)
    if args.common_wordlist:
        common.update(w.lower() for w in Path(args.common_wordlist).read_text(encoding="utf-8").splitlines())

    results = sa.analyze_batch(passwords, common)
    for r in results:
        print(f"{r.password}: severity={r.severity} entropy={r.entropy_bits} bits")
        for rec in r.recommendations:
            print(f"  - {rec}")

    compliance_results = []
    if args.breach_corpus:
        breach = cc.load_breach_corpus(args.breach_corpus)
        compliance_results = cc.check_batch(passwords, breach)
        compliant_count = sum(1 for r in compliance_results if r.compliant)
        print(f"\nNIST 800-63B compliant: {compliant_count}/{len(compliance_results)}")

    chart_paths = []
    if args.charts_dir:
        charts_dir = Path(args.charts_dir)
        charts_dir.mkdir(parents=True, exist_ok=True)
        chart_files = ["entropy_histogram.png", "severity_pie.png", "risk_ranking.png"]
        viz.plot_entropy_histogram(results, charts_dir / chart_files[0])
        viz.plot_severity_pie(results, charts_dir / chart_files[1])
        viz.plot_risk_ranking(results, charts_dir / chart_files[2])
        chart_paths = [str(charts_dir / name) for name in chart_files]
        print(f"Charts saved -> {charts_dir}")

    if args.report:
        report_text = rg.generate_report(
            results,
            compliance_results=compliance_results,
            chart_paths=chart_paths,
        )
        rg.save_report(report_text, args.report)
        print(f"\nReport saved -> {args.report}")


def cmd_verify_shadow(args: argparse.Namespace) -> None:
    creds = he.parse_shadow_file(args.shadow_file)
    wordlist = Path(args.wordlist).read_text(encoding="utf-8").splitlines()
    target = next((c for c in creds if c.username == args.username), None)
    if target is None:
        print(f"User '{args.username}' not found in {args.shadow_file}")
        return
    if target.algorithm not in cv.SCHEME_MAP:
        print(f"Algorithm '{target.algorithm}' is not supported for real crypt verification.")
        return

    result = cv.dictionary_attack_crypt(target.hash_value, target.algorithm, wordlist)
    status = "CRACKED" if result.cracked else "NOT CRACKED"
    print(f"{status} ({target.algorithm}) -- attempts={result.attempts} time={result.elapsed_seconds:.4f}s")
    if result.cracked:
        print(f"Matched password: {result.matched_word}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    if args.algorithm in bf.HASH_FUNCS:
        result = bm.benchmark_fast_hash(args.algorithm, args.duration)
    elif args.algorithm in cv.SCHEME_MAP:
        result = bm.benchmark_crypt_hash(args.algorithm, args.sample_size)
    else:
        print(f"Unknown algorithm: {args.algorithm}")
        return
    print(f"Algorithm: {result.algorithm}")
    print(f"Hashes/sec on this machine: {result.hashes_per_second:,.2f}")
    print(f"Sample count: {result.sample_count}  |  Elapsed: {result.elapsed_seconds:.4f}s")


def cmd_compliance_check(args: argparse.Namespace) -> None:
    passwords = [p for p in Path(args.input).read_text(encoding="utf-8").splitlines() if p.strip()]
    breach = cc.load_breach_corpus(args.breach_corpus)
    context_words = args.context_words.split(",") if args.context_words else []
    results = cc.check_batch(passwords, breach, context_words)
    compliant_count = sum(1 for r in results if r.compliant)
    print(f"NIST 800-63B compliant: {compliant_count}/{len(results)}\n")
    for r in results:
        print(f"{r.password}: compliant={r.compliant}")
        for v in r.violations:
            print(f"  - {v}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Password Cracking & Credential Attack Suite (ethical/simulation toolkit)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("gen-dict", help="Generate a custom wordlist")
    p_gen.add_argument("--names", help="Comma-separated seed names")
    p_gen.add_argument("--dobs", help="Comma-separated date-of-birth fragments, e.g. 1990,0190,901")
    p_gen.add_argument("--no-common", action="store_true", help="Exclude common password list")
    p_gen.add_argument("--no-keyboard", action="store_true", help="Exclude keyboard-pattern seeds")
    p_gen.add_argument("--no-leet", action="store_true", help="Disable leet-speak mutations")
    p_gen.add_argument("-o", "--output", default="wordlists/generated.txt", help="Output wordlist path")
    p_gen.set_defaults(func=cmd_gen_dict)

    p_extract = sub.add_parser("extract-hashes", help="Parse a shadow/SAM-style credential file")
    p_extract.add_argument("--format", choices=["shadow", "sam"], required=True)
    p_extract.add_argument("-i", "--input", required=True, help="Path to shadow/SAM dump file")
    p_extract.add_argument("-o", "--output", help="Optional output path for parsed credentials")
    p_extract.set_defaults(func=cmd_extract_hashes)

    p_dictattack = sub.add_parser("dict-attack", help="Simulate a dictionary attack against a hash")
    p_dictattack.add_argument("--target-hash", required=True)
    p_dictattack.add_argument("--algorithm", default="sha256", choices=list(bf.HASH_FUNCS))
    p_dictattack.add_argument("--wordlist", required=True)
    p_dictattack.set_defaults(func=cmd_dict_attack)

    p_bfest = sub.add_parser("bruteforce-estimate", help="Estimate brute-force time-to-crack")
    p_bfest.add_argument("--charsets", default="lower,upper,digits,symbols",
                          help="Comma list from: lower,upper,digits,symbols")
    p_bfest.add_argument("--min-length", type=int, default=8)
    p_bfest.add_argument("--max-length", type=int, default=8)
    p_bfest.add_argument("--guess-rate", type=int, default=bf.DEFAULT_GUESS_RATE)
    p_bfest.add_argument("--benchmark-algorithm", choices=list(bf.HASH_FUNCS),
                          help="Measure real hashes/sec on this machine and use it instead of --guess-rate")
    p_bfest.add_argument("--benchmark-duration", type=float, default=1.0)
    p_bfest.set_defaults(func=cmd_bruteforce_estimate)

    p_bfdemo = sub.add_parser("bruteforce-demo", help="Run a small real incremental brute-force demo")
    p_bfdemo.add_argument("--target-hash", required=True)
    p_bfdemo.add_argument("--algorithm", default="md5", choices=list(bf.HASH_FUNCS))
    p_bfdemo.add_argument("--charsets", default="lower,digits")
    p_bfdemo.add_argument("--max-length", type=int, default=4)
    p_bfdemo.set_defaults(func=cmd_bruteforce_demo)

    p_analyze = sub.add_parser("analyze", help="Analyze password strength for a list of passwords")
    p_analyze.add_argument("-i", "--input", required=True, help="File with one password per line")
    p_analyze.add_argument("--common-wordlist", help="Additional wordlist to treat as 'common'")
    p_analyze.add_argument("--breach-corpus", help="Path to a breach corpus for NIST 800-63B compliance checks")
    p_analyze.add_argument("--charts-dir", help="Directory to save entropy/severity/risk charts")
    p_analyze.add_argument("--report", help="Optional path to save a markdown audit report")
    p_analyze.set_defaults(func=cmd_analyze)

    p_verify = sub.add_parser("verify-shadow", help="Real dictionary attack against a Linux shadow-style crypt hash")
    p_verify.add_argument("--shadow-file", required=True)
    p_verify.add_argument("--username", required=True)
    p_verify.add_argument("--wordlist", required=True)
    p_verify.set_defaults(func=cmd_verify_shadow)

    p_bench = sub.add_parser("benchmark", help="Benchmark real hashing speed on this machine")
    p_bench.add_argument("--algorithm", required=True,
                          choices=list(bf.HASH_FUNCS) + list(cv.SCHEME_MAP))
    p_bench.add_argument("--duration", type=float, default=1.0, help="Duration (s) for fast-hash benchmarks")
    p_bench.add_argument("--sample-size", type=int, default=5, help="Sample count for slow crypt-hash benchmarks")
    p_bench.set_defaults(func=cmd_benchmark)

    p_comp = sub.add_parser("compliance-check", help="Score passwords against NIST SP 800-63B + a breach corpus")
    p_comp.add_argument("-i", "--input", required=True, help="File with one password per line")
    p_comp.add_argument("--breach-corpus", required=True)
    p_comp.add_argument("--context-words", help="Comma-separated usernames/service names to flag if reused")
    p_comp.set_defaults(func=cmd_compliance_check)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

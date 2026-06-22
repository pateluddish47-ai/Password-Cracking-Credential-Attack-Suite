"""Streamlit dashboard for the Password Cracking & Credential Attack Suite.

Run with:  streamlit run dashboard.py

Ethical, simulation-only toolkit. All hash extraction/cracking here operates
on files/text the user pastes or uploads themselves (their own lab data),
never on a live filesystem or registry.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

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

st.set_page_config(page_title="Credential Attack Suite", layout="wide", page_icon="🔐")

DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"
DEFAULT_BREACH_CORPUS = DATA_DIR / "breach_corpus.txt"


def _write_temp(text: str, suffix: str = ".txt") -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    tmp.write(text)
    tmp.close()
    return Path(tmp.name)


st.title("🔐 Password Cracking & Credential Attack Suite")
st.caption(
    "Ethical, simulation-only password policy auditing toolkit. "
    "Use only against accounts/data you own or are authorized to test."
)

(
    tab_dict,
    tab_extract,
    tab_attack,
    tab_strength,
    tab_compliance,
    tab_benchmark,
    tab_report,
) = st.tabs(
    [
        "📝 Dictionary Generator",
        "🗂️ Hash Extractor",
        "⚔️ Attack Simulator",
        "📊 Strength Analyzer",
        "✅ NIST Compliance",
        "⏱️ Live Benchmark",
        "📄 Audit Report",
    ]
)

if "strength_results" not in st.session_state:
    st.session_state.strength_results = []
if "compliance_results" not in st.session_state:
    st.session_state.compliance_results = []
if "dict_results" not in st.session_state:
    st.session_state.dict_results = []
if "bf_estimates" not in st.session_state:
    st.session_state.bf_estimates = []

# ----------------------------------------------------------------------
with tab_dict:
    st.subheader("Custom Wordlist Generator")
    col1, col2 = st.columns(2)
    with col1:
        names_in = st.text_input("Seed names (comma-separated)", "Alice,Bob")
        dobs_in = st.text_input("DOB fragments (comma-separated)", "1995,9505")
    with col2:
        include_common = st.checkbox("Include common passwords", value=True)
        include_keyboard = st.checkbox("Include keyboard patterns", value=True)
        apply_leet = st.checkbox("Apply leet-speak mutations", value=True)

    if st.button("Generate wordlist", key="gen_dict_btn"):
        names = [n.strip() for n in names_in.split(",") if n.strip()]
        dobs = [d.strip() for d in dobs_in.split(",") if d.strip()]
        words = dg.generate_wordlist(
            names=names,
            dobs=dobs,
            include_common=include_common,
            include_keyboard_patterns=include_keyboard,
            apply_leet=apply_leet,
        )
        st.session_state.generated_wordlist = words
        st.success(f"Generated {len(words)} candidate passwords.")

    if st.session_state.get("generated_wordlist"):
        words = st.session_state.generated_wordlist
        st.dataframe({"candidate": words[:200]}, height=300, use_container_width=True)
        if len(words) > 200:
            st.caption(f"Showing first 200 of {len(words)} entries.")
        st.download_button(
            "Download full wordlist (.txt)",
            data="\n".join(words),
            file_name="generated_wordlist.txt",
        )

# ----------------------------------------------------------------------
with tab_extract:
    st.subheader("Hash Extraction (Linux shadow / Windows SAM dumps)")
    fmt = st.radio("File format", ["shadow", "sam"], horizontal=True)
    upload = st.file_uploader("Upload a shadow/SAM-style file", type=["txt"])
    sample_choice = st.selectbox(
        "...or load a bundled sample",
        ["(none)", "sample_shadow.txt", "sample_sam_dump.txt"],
    )

    text = None
    if upload is not None:
        text = upload.read().decode("utf-8")
    elif sample_choice != "(none)":
        text = (DATA_DIR / sample_choice).read_text(encoding="utf-8")

    if text:
        st.text_area("File contents", text, height=150)
        if st.button("Parse credentials"):
            tmp_path = _write_temp(text)
            creds = he.parse_shadow_file(tmp_path) if fmt == "shadow" else he.parse_sam_dump(tmp_path)
            tmp_path.unlink(missing_ok=True)
            if not creds:
                st.warning("No credential entries parsed.")
            else:
                st.session_state.extracted_creds = creds
                st.success(f"Parsed {len(creds)} credential entries.")

    if st.session_state.get("extracted_creds"):
        rows = [
            {"username": c.username, "algorithm": c.algorithm, "hash": c.hash_value[:48], "source": c.source}
            for c in st.session_state.extracted_creds
        ]
        st.dataframe(rows, use_container_width=True)

# ----------------------------------------------------------------------
with tab_attack:
    st.subheader("Dictionary / Brute-Force Attack Simulation")
    st.markdown("##### 1. Dictionary attack against a raw hash digest")
    c1, c2 = st.columns(2)
    with c1:
        target_hash = st.text_input("Target hash (hex digest)", key="raw_target")
        algo = st.selectbox("Algorithm", list(bf.HASH_FUNCS), key="raw_algo")
    with c2:
        wl_text = st.text_area(
            "Wordlist (one candidate per line)",
            "\n".join(st.session_state.get("generated_wordlist", dg.COMMON_PASSWORDS)),
            height=150,
        )

    if st.button("Run dictionary attack", key="run_dict_attack"):
        wordlist = [w for w in wl_text.splitlines() if w.strip()]
        result = bf.dictionary_attack(target_hash, wordlist, algo)
        st.session_state.dict_results.append(result)
        if result.cracked:
            st.success(f"CRACKED -> '{result.matched_word}' in {result.attempts} attempts ({result.elapsed_seconds:.4f}s)")
        else:
            st.error(f"NOT CRACKED after {result.attempts} attempts ({result.elapsed_seconds:.4f}s)")

    st.markdown("---")
    st.markdown("##### 2. Real crypt-hash verification (Linux shadow style: $1$/$5$/$6$)")
    if st.session_state.get("extracted_creds"):
        shadow_creds = [c for c in st.session_state.extracted_creds if c.source == "linux_shadow"]
        if shadow_creds:
            user_choice = st.selectbox(
                "Account", [c.username for c in shadow_creds], key="crypt_user"
            )
            crypt_wl_text = st.text_area(
                "Wordlist for crypt attack",
                "\n".join(st.session_state.get("generated_wordlist", dg.COMMON_PASSWORDS)),
                height=120,
                key="crypt_wl",
            )
            if st.button("Run real crypt-hash attack"):
                target = next(c for c in shadow_creds if c.username == user_choice)
                wordlist = [w for w in crypt_wl_text.splitlines() if w.strip()]
                if target.algorithm not in cv.SCHEME_MAP:
                    st.warning(f"Algorithm '{target.algorithm}' not supported for crypt verification.")
                else:
                    result = cv.dictionary_attack_crypt(target.hash_value, target.algorithm, wordlist)
                    if result.cracked:
                        st.success(f"CRACKED -> '{result.matched_word}' in {result.attempts} attempts ({result.elapsed_seconds:.4f}s)")
                    else:
                        st.error(f"NOT CRACKED after {result.attempts} attempts ({result.elapsed_seconds:.4f}s)")
        else:
            st.info("Parse a Linux shadow file in the Hash Extractor tab first.")
    else:
        st.info("Parse a Linux shadow file in the Hash Extractor tab first.")

    st.markdown("---")
    st.markdown("##### 3. Brute-force time-to-crack estimate")
    c3, c4, c5 = st.columns(3)
    with c3:
        charsets = st.multiselect("Charsets", list(bf.CHARSETS), default=["lower", "upper", "digits", "symbols"])
    with c4:
        min_len = st.number_input("Min length", min_value=1, value=8)
        max_len = st.number_input("Max length", min_value=1, value=8)
    with c5:
        use_live = st.checkbox("Use live benchmark guess-rate", value=True)
        guess_rate = bf.DEFAULT_GUESS_RATE
        if not use_live:
            guess_rate = st.number_input("Guess rate (hashes/sec)", min_value=1, value=bf.DEFAULT_GUESS_RATE)

    if st.button("Estimate time-to-crack"):
        rate = guess_rate
        if use_live:
            bench = bm.benchmark_fast_hash("sha256", duration=0.5)
            rate = int(bench.hashes_per_second)
            st.caption(f"Live benchmark: {rate:,} sha256 hashes/sec on this machine")
        est = bf.estimate_bruteforce_time(charsets, int(min_len), int(max_len), rate)
        st.session_state.bf_estimates.append(est)
        st.metric("Estimated time to exhaust keyspace", est.estimated_human)
        st.write(f"Keyspace size: {est.keyspace_size:,}  |  Guess rate: {est.guess_rate:,}/s")

# ----------------------------------------------------------------------
with tab_strength:
    st.subheader("Password Strength Analysis")
    pw_text = st.text_area(
        "Passwords (one per line)",
        (DATA_DIR / "sample_passwords.txt").read_text(encoding="utf-8"),
        height=180,
    )
    if st.button("Analyze strength"):
        passwords = [p for p in pw_text.splitlines() if p.strip()]
        common = set(dg.COMMON_PASSWORDS)
        results = sa.analyze_batch(passwords, common)
        st.session_state.strength_results = results

    if st.session_state.strength_results:
        results = st.session_state.strength_results
        rows = [
            {
                "password": r.password,
                "length": r.length,
                "entropy_bits": r.entropy_bits,
                "severity": r.severity,
                "common": r.is_common,
                "keyboard_pattern": r.has_keyboard_pattern,
            }
            for r in results
        ]
        st.dataframe(rows, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(viz.plot_entropy_histogram(results))
        with col2:
            st.pyplot(viz.plot_severity_pie(results))
        st.pyplot(viz.plot_risk_ranking(results))

# ----------------------------------------------------------------------
with tab_compliance:
    st.subheader("NIST SP 800-63B Compliance Check (offline breach corpus)")
    context_in = st.text_input("Context words to flag (usernames/service names, comma-separated)", "")
    if st.button("Run compliance check"):
        if not st.session_state.strength_results:
            st.warning("Run the Strength Analyzer tab first to load a password list.")
        else:
            passwords = [r.password for r in st.session_state.strength_results]
            breach = cc.load_breach_corpus(DEFAULT_BREACH_CORPUS)
            context_words = [w.strip() for w in context_in.split(",") if w.strip()]
            results = cc.check_batch(passwords, breach, context_words)
            st.session_state.compliance_results = results

    if st.session_state.compliance_results:
        results = st.session_state.compliance_results
        compliant_count = sum(1 for r in results if r.compliant)
        st.metric("NIST 800-63B Compliant", f"{compliant_count}/{len(results)}")
        rows = [
            {"password": r.password, "compliant": r.compliant, "violations": "; ".join(r.violations) or "None"}
            for r in results
        ]
        st.dataframe(rows, use_container_width=True)

# ----------------------------------------------------------------------
with tab_benchmark:
    st.subheader("Live Hash-Rate Benchmark")
    st.markdown(
        "Measures real hashing throughput on **this machine** so time-to-crack "
        "estimates reflect actual hardware speed instead of a guessed constant."
    )
    bench_choice = st.selectbox("Algorithm", list(bf.HASH_FUNCS) + list(cv.SCHEME_MAP))
    if st.button("Run benchmark"):
        if bench_choice in bf.HASH_FUNCS:
            result = bm.benchmark_fast_hash(bench_choice, duration=1.0)
        else:
            result = bm.benchmark_crypt_hash(bench_choice, sample_size=5)
        st.metric(f"{result.algorithm} hashes/sec", f"{result.hashes_per_second:,.2f}")
        st.write(f"Sample count: {result.sample_count}  |  Elapsed: {result.elapsed_seconds:.4f}s")

# ----------------------------------------------------------------------
with tab_report:
    st.subheader("Generate Consolidated Audit Report")
    if not st.session_state.strength_results:
        st.info("Run the Strength Analyzer tab first.")
    else:
        if st.button("Generate report"):
            report_text = rg.generate_report(
                st.session_state.strength_results,
                dictionary_results=st.session_state.dict_results,
                bruteforce_estimates=st.session_state.bf_estimates,
                compliance_results=st.session_state.compliance_results,
            )
            st.session_state.report_text = report_text

        if st.session_state.get("report_text"):
            st.markdown(st.session_state.report_text)
            st.download_button(
                "Download report (.md)",
                data=st.session_state.report_text,
                file_name="audit_report.md",
            )

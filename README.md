# Password Cracking & Credential Attack Suite

An ethical, **simulation-only** toolkit for password policy testing and
credential security auditing, with a Streamlit dashboard, real crypt-hash
verification, live hardware benchmarking, and NIST SP 800-63B compliance
scoring on top of the four core modules from the project brief.

> This toolkit does not access live systems on its own. The hash-extraction
> module only *parses* shadow/SAM-style files that you provide (e.g. a copy
> of `/etc/shadow`, or output from tools like `samdump2`/`secretsdump.py`
> that you ran yourself in your lab). Brute-force "cracking" is either a
> mathematical time estimate, a real attack against a hash you supply, or a
> demo bounded to a tiny keyspace. Use only against accounts/data you own or
> are explicitly authorized to test.

## What makes this submission different

Most copies of this brief stop at four CLI scripts. This one adds:

| Addition | Why it matters |
|---|---|
| **Streamlit dashboard** (`password_suite/dashboard.py`) | A real interactive UI — generate wordlists, run attacks, see charts, export the report — instead of only a terminal. |
| **Real crypt-hash cracking** (`modules/crypt_verifier.py`) | Uses `passlib` to actually verify candidates against real `$1$/$5$/$6$` Linux shadow hashes, not just raw `hashlib` digests. |
| **Live hash-rate benchmark** (`modules/benchmark.py`) | Measures the actual machine's hashes/sec at runtime and feeds that real number into the time-to-crack estimate, instead of a guessed constant. |
| **NIST SP 800-63B compliance scoring** (`modules/compliance_checker.py`) | Checks passwords against a local breach corpus + length/repetition/sequence/context-word rules from the real NIST digital-identity guidelines — an actual audit framework, not just an entropy number. |
| **Visual analytics** (`modules/visualizations.py`) | Entropy histogram, severity pie chart, per-account risk ranking, embedded in both the dashboard and the markdown report. |
| **38 automated pytest tests** (`tests/`) | Every module has independently verifiable test coverage. |

## Modules

| Module | File | Purpose |
|---|---|---|
| Dictionary Generator | `password_suite/modules/dictionary_generator.py` | Builds wordlists from name/DOB seeds, common passwords, keyboard patterns, and leet-speak mutations |
| Hash Extractor | `password_suite/modules/hash_extractor.py` | Parses Linux shadow lines and Windows SAM-dump lines, identifies the hash algorithm (MD5, SHA-512, NTLM, etc.) |
| Crypt Verifier | `password_suite/modules/crypt_verifier.py` | Real `passlib`-based dictionary attack against actual crypt-style shadow hashes |
| Brute-Force Simulator | `password_suite/modules/bruteforce_simulator.py` | Dictionary-attack simulation against a raw hash, incremental brute-force keyspace estimator, and a small real demo |
| Benchmark | `password_suite/modules/benchmark.py` | Measures real hashing throughput on the current machine for both fast digests and slow crypt schemes |
| Strength Analyzer | `password_suite/modules/strength_analyzer.py` | Entropy estimate, complexity checks, common/keyboard-pattern detection, severity rating |
| Compliance Checker | `password_suite/modules/compliance_checker.py` | NIST SP 800-63B scoring against a local breach corpus, repetition/sequence/context-word checks |
| Visualizations | `password_suite/modules/visualizations.py` | Entropy histogram, severity pie chart, risk-ranking bar chart |
| Report Generator | `password_suite/modules/report_generator.py` | Combines all results into a markdown audit report with embedded charts and policy recommendations |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Dashboard (recommended for live demos)

```bash
source .venv/bin/activate
cd password_suite
streamlit run dashboard.py
```

Opens a browser UI with tabs for: Dictionary Generator, Hash Extractor,
Attack Simulator (raw-hash dictionary attack, real crypt-hash attack,
brute-force estimate with live benchmark), Strength Analyzer (with charts),
NIST Compliance, Live Benchmark, and a downloadable Audit Report.

## CLI usage

```bash
cd password_suite

# 1. Generate a custom wordlist
python3 main.py gen-dict --names "Alice,Bob" --dobs "1995,9505" -o ../wordlists/generated.txt

# 2. Parse hash dumps (sample files included under sample_data/)
python3 main.py extract-hashes --format shadow -i ../sample_data/sample_shadow.txt
python3 main.py extract-hashes --format sam -i ../sample_data/sample_sam_dump.txt

# 3a. Simulate a dictionary attack against a raw hash digest
python3 main.py dict-attack --target-hash <hash> --algorithm sha256 --wordlist ../wordlists/generated.txt

# 3b. Real attack against an actual Linux shadow-style crypt hash
python3 main.py verify-shadow --shadow-file ../sample_data/sample_shadow.txt --username alice --wordlist ../wordlists/generated.txt

# 3c. Estimate brute-force time-to-crack, using a live-measured guess rate
python3 main.py bruteforce-estimate --charsets lower,upper,digits,symbols --min-length 8 --max-length 8 --benchmark-algorithm sha256

# 3d. Tiny real incremental brute-force demo (max-length kept small intentionally)
python3 main.py bruteforce-demo --target-hash <hash> --algorithm md5 --charsets lower,digits --max-length 4

# 4. Benchmark real hashing speed on this machine
python3 main.py benchmark --algorithm sha256 --duration 1
python3 main.py benchmark --algorithm SHA-512 --sample-size 5

# 5. NIST 800-63B compliance check against a local breach corpus
python3 main.py compliance-check -i ../sample_data/sample_passwords.txt --breach-corpus ../sample_data/breach_corpus.txt --context-words alice,bob

# 6. Full strength analysis + compliance + charts + audit report
python3 main.py analyze -i ../sample_data/sample_passwords.txt \
  --breach-corpus ../sample_data/breach_corpus.txt \
  --charts-dir ../reports/charts \
  --report ../reports/audit_report.md
```

## Tests

```bash
source .venv/bin/activate
python3 -m pytest tests/ -v
```

## Directory layout

```
password_suite/         CLI + dashboard + module source code
sample_data/             Sample shadow / SAM / password / breach-corpus files
wordlists/               Generated wordlists land here
reports/                 Generated audit reports + charts land here
tests/                   pytest suite (one file per module)
```

## Sample hash identifiers

| Prefix | Algorithm |
|---|---|
| `$1$` | MD5 crypt |
| `$5$` | SHA-256 crypt |
| `$6$` | SHA-512 crypt |
| `$y$` | yescrypt |
| no `$` prefix | legacy DES crypt |
| 32-hex-char in SAM dump field 4 | NTLM (MD4 of UTF-16LE password) |

## NIST SP 800-63B compliance rules implemented

- Minimum length 8 characters (NIST sets 8 as the floor, recommends allowing up to 64, and deliberately does **not** mandate composition rules)
- Reject passwords matching a known compromised/commonly-used list (local offline breach corpus, `sample_data/breach_corpus.txt` — no network calls)
- Flag repetitive character runs (e.g. `aaaa`)
- Flag sequential character runs (e.g. `1234`, `abcd`)
- Flag context-specific words (username/service name reused in the password)

## Recommended password policy (also emitted in generated reports)

- Minimum length 12 (14+ for privileged accounts)
- Require uppercase, lowercase, digits, and symbols
- Block known-breached/common passwords
- Lockout/rate-limit after repeated failures
- Store credentials with bcrypt/scrypt/Argon2 — never unsalted MD5/SHA1
- Enforce MFA wherever possible

## Still on you before submission

This repo covers the **code** deliverable end-to-end. The brief also asks for
non-code deliverables not covered here: screenshots of each module/dashboard
tab running, a Draw.io flowchart of the architecture, the formal Word/PDF
project report, and the final PPT.

"""Generates the formal project report (Word .docx) for GTU submission."""
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
CHARTS = REPORTS / "charts"
SCREENSHOTS = REPORTS / "screenshots"
LIVE_APP_URL = "https://password-cracking-credential-attack-suite-58xby2nrznzkhogifexp.streamlit.app/"
REPO_URL = "https://github.com/pateluddish47-ai/Password-Cracking-Credential-Attack-Suite"

NAVY = RGBColor(0x1E, 0x3A, 0x5F)
GRAY = RGBColor(0x44, 0x44, 0x44)

doc = Document()

# ---------- base style ----------
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

# ---------- title page ----------
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("Password Cracking & Credential Attack Suite")
run.bold = True
run.font.size = Pt(28)
run.font.color.rgb = NAVY

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run("An Ethical, Simulation-Only Toolkit for Password Policy Testing\nand Credential Security Auditing")
run.italic = True
run.font.size = Pt(13)
run.font.color.rgb = GRAY

for _ in range(4):
    doc.add_paragraph()

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = meta.add_run("Prepared by\nUddish Patel")
run.bold = True
run.font.size = Pt(16)

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_p.add_run(date.today().strftime("%B %Y"))
run.font.size = Pt(12)
run.font.color.rgb = GRAY

doc.add_paragraph()
link_p = doc.add_paragraph()
link_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = link_p.add_run(f"Live application: {LIVE_APP_URL}")
run.font.size = Pt(11)
run.font.color.rgb = NAVY
link_p2 = doc.add_paragraph()
link_p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = link_p2.add_run(f"Source code: {REPO_URL}")
run.font.size = Pt(11)
run.font.color.rgb = NAVY

doc.add_page_break()


def heading(text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.color.rgb = NAVY
    return h


def body(text):
    p = doc.add_paragraph(text)
    p.style.font.size = Pt(11)
    return p


def bullet(text):
    doc.add_paragraph(text, style="List Bullet")


# ---------- 1. Abstract ----------
heading("1. Abstract", 1)
body(
    "Weak passwords remain one of the most exploited vulnerabilities in cybersecurity. "
    "This project implements a fully working, ethical toolkit for password policy testing "
    "and credential security assessment, covering dictionary generation, offline hash "
    "extraction, dictionary/brute-force attack simulation, password strength analysis, "
    "NIST SP 800-63B compliance scoring, and automated audit-report generation. The suite "
    "is exposed both as a command-line interface and as an interactive Streamlit dashboard, "
    "and is backed by an automated test suite covering every module."
)

# ---------- 2. Introduction ----------
heading("2. Introduction & Practical Motivation", 1)
body(
    "Passwords remain the first line of defense for user authentication. Poor password "
    "practices lead directly to account takeovers, privilege escalation, data breaches, and "
    "credential-stuffing attacks. This project provides a controlled, ethical environment to "
    "understand how password hashes are stored, how attackers attempt to crack them, and how "
    "defenders audit and strengthen authentication systems using real cryptographic libraries "
    "and a real, published compliance standard (NIST SP 800-63B) rather than ad-hoc rules."
)

# ---------- 3. Objectives ----------
heading("3. Project Objectives", 1)
for line in [
    "Develop a dictionary generator for password testing, including pattern-based seeds and mutation rules.",
    "Extract and identify password hashes from Linux shadow files and Windows SAM-style dumps (offline, ethical scope only).",
    "Build a brute-force and dictionary-attack simulation engine, including real cryptographic verification.",
    "Analyze password strength based on complexity, entropy, and predictability.",
    "Score passwords against the NIST SP 800-63B digital identity guideline and a local breach corpus.",
    "Generate a detailed, visual audit report on password vulnerabilities and mitigation steps.",
    "Expose all of the above through both a CLI and an interactive dashboard.",
]:
    bullet(line)

# ---------- 4. Scope ----------
heading("4. Scope of the Project", 1)
scope_items = [
    ("Dictionary Generator", "Generates custom wordlists from name/DOB seeds, common passwords, keyboard "
     "patterns, and leet-speak/case/suffix mutations."),
    ("Hash Extraction", "Parses Linux /etc/shadow-style lines and Windows SAM-dump lines supplied by the "
     "user, and identifies the hashing algorithm in use (MD5, SHA-256, SHA-512, yescrypt, NTLM, LM)."),
    ("Attack Simulation", "Runs a dictionary attack against raw hash digests, a real passlib-based "
     "dictionary attack against actual Linux crypt hashes, a bounded incremental brute-force demo, "
     "and a mathematical brute-force time-to-crack estimator calibrated against a live hash-rate "
     "benchmark of the host machine."),
    ("Strength Analysis", "Computes Shannon-style entropy, checks composition, flags common/keyboard-walk "
     "passwords, and assigns a Critical/High/Medium/Low severity rating."),
    ("Compliance Scoring", "Checks each password against NIST SP 800-63B requirements: minimum length, "
     "breach-corpus membership, repetitive/sequential character runs, and context-specific word reuse."),
    ("Reporting", "Produces a Markdown audit report with summary statistics, attack results, compliance "
     "results, embedded charts, and a recommended password policy."),
]
table = doc.add_table(rows=1, cols=2)
table.style = "Light Grid Accent 1"
hdr = table.rows[0].cells
hdr[0].text, hdr[1].text = "Module", "Description"
for name, desc in scope_items:
    row = table.add_row().cells
    row[0].text, row[1].text = name, desc

doc.add_paragraph()

# ---------- 5. Tools ----------
heading("5. Tools & Technologies Used", 1)
bullet("Python 3 -- core implementation language")
bullet("hashlib -- MD5/SHA-1/SHA-256/SHA-512 digest operations")
bullet("passlib -- real crypt-style hash generation and verification ($1$/$5$/$6$, bcrypt)")
bullet("Streamlit -- interactive web dashboard")
bullet("Matplotlib -- entropy histogram, severity pie chart, risk-ranking chart")
bullet("pytest -- automated unit test suite (38 tests across 8 modules)")
bullet("NIST SP 800-63B (Digital Identity Guidelines) -- compliance reference standard")

# ---------- 6. Architecture ----------
heading("6. System Architecture / Workflow", 1)
body(
    "The toolkit follows a linear audit pipeline: user-supplied input feeds the dictionary "
    "generator, hash extractor, and attack/analysis modules, whose outputs are consolidated "
    "into a single audit report. The figure below illustrates the end-to-end workflow."
)
flowchart_path = REPORTS / "flowchart.png"
if flowchart_path.exists():
    doc.add_picture(str(flowchart_path), width=Inches(5.3))
    cap = doc.add_paragraph("Figure 1: System architecture / workflow")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].italic = True

doc.add_page_break()

# ---------- 7. Live application & screenshots ----------
heading("7. Live Application & Screenshots", 1)
body(
    f"The dashboard is deployed and publicly accessible at: {LIVE_APP_URL}\n"
    f"Source code repository: {REPO_URL}\n\n"
    "The screenshots below were captured directly from the live deployment "
    "(not a local mockup), with each tab's primary action executed so the "
    "actual output is visible."
)

screenshot_figures = [
    ("00_home.png", "Figure A: Dashboard home screen with all seven functional tabs"),
    ("01_Dictionary_Generator.png", "Figure B: Dictionary Generator -- 1,158 candidate passwords generated from name/DOB seeds"),
    ("02_Hash_Extractor.png", "Figure C: Hash Extractor -- parsed Linux shadow file with algorithm identification"),
    ("03_Attack_Simulator.png", "Figure D: Attack Simulator -- dictionary attack, real crypt-hash attack, and brute-force time-to-crack estimate"),
    ("04_Strength_Analyzer.png", "Figure E: Strength Analyzer -- entropy table with entropy histogram, severity pie chart, and risk ranking"),
    ("05_NIST_Compliance.png", "Figure F: NIST SP 800-63B Compliance Check -- 6/10 compliant with itemized violations"),
    ("06_Live_Benchmark.png", "Figure G: Live Benchmark -- real measured MD5 throughput on the host machine"),
    ("07_Audit_Report.png", "Figure H: Consolidated Audit Report generated and rendered in-app"),
]
for img_name, caption in screenshot_figures:
    img_path = SCREENSHOTS / img_name
    if img_path.exists():
        doc.add_picture(str(img_path), width=Inches(5.6))
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].italic = True
        doc.add_paragraph()

doc.add_page_break()

# ---------- 8. Differentiators ----------
heading("8. Key Differentiators", 1)
body(
    "Beyond the four baseline modules, this implementation adds the following to demonstrate "
    "depth of understanding rather than a surface-level reproduction of the brief:"
)
bullet("A fully interactive Streamlit dashboard with seven functional tabs, not just a CLI.")
bullet("Real cryptographic verification against actual Linux crypt hashes using passlib, in addition to raw-digest simulation.")
bullet("A live hash-rate benchmark that measures this machine's real throughput and feeds it into time-to-crack estimates, instead of relying on a guessed constant.")
bullet("Compliance scoring against the published NIST SP 800-63B standard with an offline breach corpus, repetition/sequence/context-word checks.")
bullet("Visual analytics (entropy histogram, severity pie chart, per-account risk ranking) embedded in both the dashboard and the generated report.")
bullet("A 38-test automated pytest suite covering every module, independently verifiable by re-running `pytest tests/`.")

# ---------- 8. Results ----------
heading("9. Results & Demonstration", 1)
body(
    "The toolkit was exercised end-to-end against the bundled sample data "
    "(sample_data/sample_shadow.txt, sample_sam_dump.txt, sample_passwords.txt, "
    "breach_corpus.txt). A summary of the strength-analysis run is shown below."
)

results_table_data = [
    ("password123", "11", "56.87", "Medium"),
    ("qwerty12", "8", "41.36", "High"),
    ("P@ssw0rd!2025", "13", "85.41", "Low"),
    ("123456", "6", "19.93", "Critical"),
    ("Tr0ub4dor&3", "11", "72.27", "Low"),
    ("admin", "5", "23.50", "Critical"),
    ("correcthorsebatterystaple", "25", "117.51", "Low"),
    ("Summer2026!", "11", "72.27", "Low"),
    ("letmein1", "8", "41.36", "Medium"),
    ("Xk9$mQ2#vL8pR4z", "15", "98.55", "Low"),
]
res_table = doc.add_table(rows=1, cols=4)
res_table.style = "Light Grid Accent 1"
hdr = res_table.rows[0].cells
for i, label in enumerate(["Password", "Length", "Entropy (bits)", "Severity"]):
    hdr[i].text = label
for row_data in results_table_data:
    row = res_table.add_row().cells
    for i, val in enumerate(row_data):
        row[i].text = val

doc.add_paragraph()
body("NIST SP 800-63B compliance result for the same sample set: 6 of 10 passwords compliant; "
     "the 4 non-compliant entries were rejected for matching the local breach corpus, being "
     "below the 8-character minimum, or containing a sequential character run.")

for img_name, caption in [
    ("entropy_histogram.png", "Figure 2: Password entropy distribution"),
    ("severity_pie.png", "Figure 3: Severity distribution across the sample set"),
    ("risk_ranking.png", "Figure 4: Per-account risk ranking (lowest entropy = highest risk)"),
]:
    img_path = CHARTS / img_name
    if img_path.exists():
        doc.add_picture(str(img_path), width=Inches(4.6))
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].italic = True

doc.add_page_break()

# ---------- 9. Real attack demonstration ----------
heading("10. Real Attack Demonstration", 1)
body(
    "Unlike a purely theoretical exercise, this toolkit was verified against real, "
    "freshly generated crypt hashes. A SHA-512-crypt hash for user 'alice' (sample_shadow.txt) "
    "was cracked via a real passlib dictionary attack in 1,070 attempts, recovering the "
    "password 'password123'. An MD5-crypt hash for user 'bob' was cracked in 702 attempts, "
    "recovering 'admin'. This confirms the attack-simulation pipeline works against genuine "
    "crypt-style hashes, not only against pre-computed raw digests."
)

# ---------- 10. NIST methodology ----------
heading("11. NIST SP 800-63B Compliance Methodology", 1)
body("The compliance checker implements the following requirements from the NIST Digital Identity Guidelines:")
bullet("Minimum length of 8 characters (NIST sets 8 as the floor and recommends allowing up to 64).")
bullet("No mandatory composition rules (NIST deliberately does not require mixed-case/digit/symbol composition).")
bullet("Verifiers SHALL reject secrets found on a list of known compromised or commonly used values -- implemented via a local, offline breach corpus.")
bullet("Repetitive character sequences (e.g. 'aaaa') and sequential sequences (e.g. '1234', 'abcd') are flagged.")
bullet("Context-specific words (e.g. username or service name reused in the password) are flagged.")

# ---------- 11. Ethical considerations ----------
heading("12. Security & Ethical Considerations", 1)
bullet("All hash extraction operates on files supplied by the user; no live filesystem or registry access is performed.")
bullet("Brute-force 'cracking' is bounded to small demo keyspaces or backed by a mathematical estimate -- not unrestricted live cracking.")
bullet("The breach corpus is a small, locally curated list of well-known common/breached passwords; no live network lookups are made.")
bullet("Intended for use only against accounts and data the user owns or is explicitly authorized to test.")

# ---------- 12. Learning outcomes ----------
heading("13. Learning Outcomes", 1)
bullet("Practical understanding of how passwords are stored, hashed, and protected on Linux and Windows.")
bullet("Hands-on experience with ethical password-cracking methodologies and their real time/compute cost.")
bullet("Applied a real, published authentication security standard (NIST SP 800-63B) rather than ad-hoc heuristics.")
bullet("Red-team vs blue-team perspective: building both the attack simulation and the defensive audit/reporting side.")
bullet("End-to-end software engineering: modular design, a CLI, an interactive dashboard, and automated testing.")

# ---------- 13. Conclusion ----------
heading("14. Conclusion & Future Scope", 1)
body(
    "This project delivers a complete, working, and ethically scoped password-auditing toolkit "
    "that goes beyond a basic script collection: it includes a real interactive dashboard, "
    "genuine cryptographic hash verification, a measured (not guessed) brute-force time "
    "estimate, and compliance scoring against a real published standard. Future extensions "
    "could include integrating a live k-anonymity breach-check API (e.g. Have I Been Pwned), "
    "GPU-accelerated benchmarking, and multi-user audit history storage."
)

# ---------- 14. References ----------
heading("15. References", 1)
bullet("NIST Special Publication 800-63B -- Digital Identity Guidelines: Authentication and Lifecycle Management.")
bullet("passlib documentation -- https://passlib.readthedocs.io")
bullet("Streamlit documentation -- https://docs.streamlit.io")
bullet("Python hashlib documentation -- https://docs.python.org/3/library/hashlib.html")

out_path = REPORTS / "Project_Report_Uddish_Patel.docx"
doc.save(str(out_path))
print(f"saved {out_path}")

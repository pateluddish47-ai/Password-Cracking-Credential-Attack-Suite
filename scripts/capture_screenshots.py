"""Captures real screenshots of the live deployed Streamlit dashboard.

Each scenario loads a fresh page and only ever switches tabs forward
(never back), since Streamlit's iframe re-renders made backward tab
switches on a long-lived page flaky to automate reliably. Each action
button is actually clicked, so screenshots show genuine results.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://password-cracking-credential-attack-suite-58xby2nrznzkhogifexp.streamlit.app/"
OUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_PASSWORDS = (
    "password123\nqwerty12\nP@ssw0rd!2025\n123456\nTr0ub4dor&3\n"
    "admin\ncorrecthorsebatterystaple\nSummer2026!\nletmein1\nXk9$mQ2#vL8pR4z"
)


def wake_if_asleep(page):
    page.wait_for_timeout(3000)
    for label in ["Yes, get this app back up!", "Get this app back up"]:
        try:
            btn = page.get_by_text(label, exact=False)
            if btn.count() > 0:
                print(f"  app asleep, clicking wake button: {label}")
                btn.first.click()
                page.wait_for_timeout(30000)
                break
        except Exception:
            pass


def get_app_frame(page):
    for f in page.frames:
        if "/~/+/" in f.url:
            return f
    return page


def click_button(frame, text, timeout=20000):
    btn = frame.get_by_role("button", name=text, exact=False).first
    btn.wait_for(state="visible", timeout=timeout)
    btn.scroll_into_view_if_needed()
    btn.click()


def select_dropdown_option(frame, page, option_text, select_index=0, retries=3):
    last_err = None
    for _ in range(retries):
        try:
            select = frame.locator('[data-baseweb="select"]:visible').nth(select_index)
            select.wait_for(state="visible", timeout=15000)
            select.scroll_into_view_if_needed()
            select.click(force=True, timeout=15000)
            page.wait_for_timeout(400)
            page.keyboard.type(option_text)
            page.wait_for_timeout(400)
            page.keyboard.press("Enter")
            page.wait_for_timeout(800)
            return
        except Exception as e:
            last_err = e
            page.wait_for_timeout(1500)
    raise last_err


def fill_by_label(frame, label, text, tag="textarea", timeout=20000):
    el = frame.locator(f'{tag}[aria-label="{label}"]').first
    el.wait_for(state="visible", timeout=timeout)
    el.scroll_into_view_if_needed()
    el.fill(text)


def goto_tab(frame, page, label):
    frame.get_by_text(label, exact=False).first.click()
    page.wait_for_timeout(2000)


def new_app_page(browser):
    page = browser.new_page(viewport={"width": 1440, "height": 2600})
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    wake_if_asleep(page)
    page.wait_for_timeout(10000)
    try:
        page.wait_for_selector("text=Password Cracking", timeout=60000)
    except Exception:
        print("  title text not found yet, continuing anyway")
    page.wait_for_timeout(4000)
    return page, get_app_frame(page)


def snap(page, name):
    page.screenshot(path=str(OUT_DIR / name), full_page=True)
    print(f"saved {name}")


def run_scenario(browser, name, fn, retries=3):
    print(f"--- scenario: {name} ---")
    last_err = None
    for attempt in range(retries):
        page = None
        try:
            page, frame = new_app_page(browser)
            fn(page, frame)
            page.close()
            return
        except Exception as e:
            last_err = e
            print(f"  attempt {attempt + 1} failed: {e}")
            if page is not None:
                page.close()
            import time

            time.sleep(5)
    print(f"  scenario '{name}' failed after {retries} attempts: {last_err}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        def home(page, frame):
            snap(page, "00_home.png")

        def dict_generator(page, frame):
            goto_tab(frame, page, "Dictionary Generator")
            click_button(frame, "Generate wordlist")
            page.wait_for_timeout(3000)
            snap(page, "01_Dictionary_Generator.png")

        def hash_extractor_shadow(page, frame):
            goto_tab(frame, page, "Hash Extractor")
            select_dropdown_option(frame, page, "sample_shadow.txt")
            click_button(frame, "Parse credentials")
            page.wait_for_timeout(2000)
            snap(page, "02a_Hash_Extractor_Shadow.png")

        def hash_extractor_sam(page, frame):
            goto_tab(frame, page, "Hash Extractor")
            frame.get_by_text("sam", exact=True).first.click()
            page.wait_for_timeout(800)
            select_dropdown_option(frame, page, "sample_sam_dump.txt")
            click_button(frame, "Parse credentials")
            page.wait_for_timeout(2000)
            snap(page, "02b_Hash_Extractor_SAM.png")

        def attack_dict(page, frame):
            import hashlib

            goto_tab(frame, page, "Attack Simulator")
            target = hashlib.sha256(b"password123").hexdigest()
            fill_by_label(frame, "Target hash (hex digest)", target, tag="input")
            fill_by_label(frame, "Wordlist (one candidate per line)", SAMPLE_PASSWORDS)
            click_button(frame, "Run dictionary attack")
            page.wait_for_timeout(2500)
            snap(page, "03a_Attack_Simulator_DictAttack.png")

        def attack_crypt(page, frame):
            goto_tab(frame, page, "Hash Extractor")
            select_dropdown_option(frame, page, "sample_shadow.txt")
            click_button(frame, "Parse credentials")
            page.wait_for_timeout(2000)

            goto_tab(frame, page, "Attack Simulator")
            select_dropdown_option(frame, page, "root")
            fill_by_label(frame, "Wordlist for crypt attack", SAMPLE_PASSWORDS)
            click_button(frame, "Run real crypt-hash attack")
            page.wait_for_timeout(3000)
            snap(page, "03b_Attack_Simulator_CryptAttack.png")

        def attack_bruteforce(page, frame):
            goto_tab(frame, page, "Attack Simulator")
            click_button(frame, "Estimate time-to-crack")
            page.wait_for_timeout(3000)
            snap(page, "03c_Attack_Simulator_BruteForce.png")

        def strength_analyzer(page, frame):
            goto_tab(frame, page, "Strength Analyzer")
            click_button(frame, "Analyze strength")
            page.wait_for_timeout(6000)
            snap(page, "04_Strength_Analyzer.png")

        def nist_compliance(page, frame):
            goto_tab(frame, page, "Strength Analyzer")
            click_button(frame, "Analyze strength")
            page.wait_for_timeout(4000)
            goto_tab(frame, page, "NIST Compliance")
            click_button(frame, "Run compliance check")
            page.wait_for_timeout(2500)
            snap(page, "05_NIST_Compliance.png")

        def live_benchmark(page, frame):
            goto_tab(frame, page, "Live Benchmark")
            click_button(frame, "Run benchmark")
            page.wait_for_timeout(2500)
            snap(page, "06_Live_Benchmark.png")

        def audit_report(page, frame):
            goto_tab(frame, page, "Strength Analyzer")
            click_button(frame, "Analyze strength")
            page.wait_for_timeout(4000)
            goto_tab(frame, page, "Audit Report")
            click_button(frame, "Generate report")
            page.wait_for_timeout(4000)
            snap(page, "07_Audit_Report.png")

        scenarios = [
            ("home", home),
            ("dictionary generator", dict_generator),
            ("hash extractor (shadow)", hash_extractor_shadow),
            ("hash extractor (sam)", hash_extractor_sam),
            ("attack simulator (dict attack)", attack_dict),
            ("attack simulator (crypt attack)", attack_crypt),
            ("attack simulator (bruteforce estimate)", attack_bruteforce),
            ("strength analyzer", strength_analyzer),
            ("nist compliance", nist_compliance),
            ("live benchmark", live_benchmark),
            ("audit report", audit_report),
        ]
        for name, fn in scenarios:
            run_scenario(browser, name, fn)

        browser.close()


if __name__ == "__main__":
    main()

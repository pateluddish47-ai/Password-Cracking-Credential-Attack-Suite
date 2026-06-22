"""Captures real screenshots of the live deployed Streamlit dashboard,
running each tab's primary action first so the screenshots show actual
results (parsed hashes, charts, compliance results) instead of blank forms.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://password-cracking-credential-attack-suite-58xby2nrznzkhogifexp.streamlit.app/"
OUT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def click_button(frame, text):
    btn = frame.get_by_role("button", name=text, exact=False).first
    btn.scroll_into_view_if_needed()
    btn.click()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 2400})
        print(f"navigating to {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(15000)
        try:
            page.wait_for_selector("text=Password Cracking", timeout=60000)
        except Exception:
            print("title text not found yet, continuing anyway")
        page.wait_for_timeout(5000)

        app_frame = page
        for f in page.frames:
            if "/~/+/" in f.url:
                app_frame = f
                break
        print(f"using frame: {getattr(app_frame, 'url', 'main page')}")

        page.screenshot(path=str(OUT_DIR / "00_home.png"), full_page=True)
        print("saved 00_home.png")

        def goto_tab(label):
            app_frame.get_by_text(label, exact=False).first.click()
            page.wait_for_timeout(2000)

        def snap(name):
            page.screenshot(path=str(OUT_DIR / name), full_page=True)
            print(f"saved {name}")

        # 1. Dictionary Generator -> generate a wordlist
        goto_tab("Dictionary Generator")
        try:
            click_button(app_frame, "Generate wordlist")
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"dict-gen action failed: {e}")
        snap("01_Dictionary_Generator.png")

        # 2. Hash Extractor -> load bundled sample + parse
        goto_tab("Hash Extractor")
        try:
            select = app_frame.locator('[data-baseweb="select"]').first
            select.click()
            page.wait_for_timeout(500)
            app_frame.get_by_text("sample_shadow.txt", exact=False).first.click()
            page.wait_for_timeout(1000)
            click_button(app_frame, "Parse credentials")
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"hash-extract action failed: {e}")
        snap("02_Hash_Extractor.png")

        # 3. Attack Simulator -> brute-force estimate
        goto_tab("Attack Simulator")
        try:
            click_button(app_frame, "Estimate time-to-crack")
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"attack-sim action failed: {e}")
        snap("03_Attack_Simulator.png")

        # 4. Strength Analyzer -> analyze
        goto_tab("Strength Analyzer")
        try:
            click_button(app_frame, "Analyze strength")
            page.wait_for_timeout(6000)
        except Exception as e:
            print(f"strength action failed: {e}")
        snap("04_Strength_Analyzer.png")

        # 5. NIST Compliance -> run check (depends on strength results from previous tab)
        goto_tab("NIST Compliance")
        try:
            click_button(app_frame, "Run compliance check")
            page.wait_for_timeout(2500)
        except Exception as e:
            print(f"compliance action failed: {e}")
        snap("05_NIST_Compliance.png")

        # 6. Live Benchmark -> run benchmark
        goto_tab("Live Benchmark")
        try:
            click_button(app_frame, "Run benchmark")
            page.wait_for_timeout(2500)
        except Exception as e:
            print(f"benchmark action failed: {e}")
        snap("06_Live_Benchmark.png")

        # Re-run strength analysis right before the report tab in case session
        # state was reset by an intermediate app rerun.
        goto_tab("Strength Analyzer")
        try:
            click_button(app_frame, "Analyze strength")
            page.wait_for_timeout(5000)
        except Exception as e:
            print(f"strength re-run failed: {e}")

        # 7. Audit Report -> generate report
        goto_tab("Audit Report")
        try:
            click_button(app_frame, "Generate report")
            page.wait_for_timeout(4000)
        except Exception as e:
            print(f"report action failed: {e}")
        snap("07_Audit_Report.png")

        browser.close()


if __name__ == "__main__":
    main()

"""Браузерный e2e для SOC-панели: карта, точки, KPI, фильтры, импорт, офлайн."""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8000/"
errors, external = [], []


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))

        def on_req(r):
            u = r.url
            if not (u.startswith("http://localhost") or u.startswith("data:") or u.startswith("blob:")):
                external.append(u)
        pg.on("request", on_req)

        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_timeout(1500)

        countries = pg.eval_on_selector_all(".country", "els => els.length")
        points = pg.eval_on_selector_all(".pt", "els => els.length")
        kpi_attacks = pg.inner_text("#kpiAttacks")
        kpi_ips = pg.inner_text("#kpiIps")
        kpi_countries = pg.inner_text("#kpiCountries")
        bars = pg.eval_on_selector_all("#bars .bar", "els => els.length")

        # клик по точке -> попап
        pg.eval_on_selector(".pt", "el => el.dispatchEvent(new MouseEvent('click', {bubbles:true, clientX:200, clientY:200}))")
        pg.wait_for_timeout(300)
        popup = pg.is_visible("#popup")

        # фильтр: выключить critical
        before = pg.eval_on_selector_all(".pt", "els => els.length")
        pg.click('.chip[data-sev="critical"]')
        pg.wait_for_timeout(300)
        after_filter = pg.eval_on_selector_all(".pt", "els => els.length")
        pg.click('.chip[data-sev="critical"]')  # вернуть

        # слайдер threat-score
        pg.eval_on_selector("#scoreSlider", "el => { el.value = el.max; el.dispatchEvent(new Event('input')); }")
        pg.wait_for_timeout(300)
        after_slider = pg.eval_on_selector_all(".pt", "els => els.length")
        pg.eval_on_selector("#scoreSlider", "el => { el.value = 0; el.dispatchEvent(new Event('input')); }")

        # live log тикает
        pg.wait_for_timeout(4500)
        log = pg.eval_on_selector_all("#log .e", "els => els.length")

        b.close()

        print(f"countries={countries} points={points}")
        print(f"KPI: attacks={kpi_attacks} ips={kpi_ips} countries={kpi_countries}")
        print(f"bars={bars} popup={popup}")
        print(f"filter critical-off: {before} -> {after_filter}")
        print(f"slider max: -> {after_slider}")
        print(f"log entries after ~4.5s: {log}")
        print(f"console errors: {errors}")
        print(f"external requests: {external}")

        ok = (countries > 100 and points == 100 and bars > 0 and popup
              and after_filter < before and after_slider < before
              and log >= 1 and not errors and not external
              and kpi_ips == "100")
        print("RESULT:", "PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)


run()

"""E2E mobile portrait: проверить адаптивную раскладку SOC-карты на телефоне."""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8010"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # iPhone 12-ish портрет
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    errors, external = [], []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("request", lambda r: external.append(r.url)
            if not r.url.startswith(BASE) and not r.url.startswith("data:") else None)
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("g.hotspot", timeout=10000)
    page.wait_for_timeout(1200)

    # геометрия: есть ли горизонтальный оверфлоу (плохо для мобилы)
    metrics = page.evaluate("""() => {
      const map = document.getElementById('map').getBoundingClientRect();
      return {
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
        mapW: Math.round(map.width), mapH: Math.round(map.height),
        hotspots: document.querySelectorAll('g.hotspot').length,
        kpiCols: getComputedStyle(document.querySelector('.kpis')).gridTemplateColumns,
        mainCols: getComputedStyle(document.querySelector('.main')).gridTemplateColumns,
      };
    }""")
    page.screenshot(path="e2e_mobile_portrait.png", full_page=True)

    # тап по хотспоту -> попап
    page.locator("g.hotspot").first.click()
    page.wait_for_timeout(400)
    tip_shown = page.locator("#tip.show").count() == 1
    page.screenshot(path="e2e_mobile_tip.png")
    browser.close()

    metrics["horizontal_overflow"] = metrics["scrollW"] > metrics["clientW"] + 1
    metrics["tip_on_tap"] = tip_shown
    metrics["console_errors"] = errors
    metrics["external_requests"] = external
    print(metrics)

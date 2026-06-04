"""E2E: проверить SOC-карту угроз — рендер, KPI, фильтры, офлайн (ноль внешних запросов)."""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8010"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 810})
    errors, external = [], []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("request", lambda r: external.append(r.url)
            if not r.url.startswith(BASE) and not r.url.startswith("data:") else None)
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("g.hotspot", timeout=10000)
    page.wait_for_timeout(1500)

    hotspots = page.locator("g.hotspot").count()
    kpis = {k: page.locator(f"#{k}").inner_text()
            for k in ["kAttacks", "kIps", "kCountries", "kCrit"]}
    bars = page.locator(".bar").count()

    # фильтр: выключаем low/medium/high -> остаются только critical
    for sev in ["low", "medium", "high"]:
        page.click(f'.chip[data-sev="{sev}"]')
    page.wait_for_timeout(700)
    hotspots_crit = page.locator("g.hotspot").count()

    # threat-score slider -> поднимаем порог
    page.eval_on_selector("#score", "el => { el.value = 4000; el.dispatchEvent(new Event('input')); }")
    page.wait_for_timeout(500)
    hotspots_high_score = page.locator("g.hotspot").count()

    page.screenshot(path="e2e_screenshot.png")
    log_after = page.locator("#log .ev").count()
    browser.close()

    print({
        "hotspots_all": hotspots,
        "kpis": kpis,
        "top_bars": bars,
        "hotspots_critical_only": hotspots_crit,
        "hotspots_critical_score>=4000": hotspots_high_score,
        "live_log_events": log_after,
        "console_errors": errors,
        "external_requests": external,
    })

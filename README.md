# Тепловая карта вредоносных IP — SOC-панель

Интерактивная тепловая карта киберугроз на векторной карте мира. Всё работает
в браузере на синтетических данных: без бэкенда-логики, без сети, без тайлов.
D3 + TopoJSON, неоновые точки-хотспоты, KPI, фильтры, Топ-5 стран, live-лента
событий и импорт JSON/CSV — целиком офлайн.

## Запуск локально

```bash
uv venv
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Открыть http://localhost:8000

## Структура

- `static/index.html` — весь фронт (inline CSS + vanilla JS).
- `static/vendor/` — локальные D3, topojson-client, атлас мира TopoJSON (без CDN).
- `static/data/threats.json` — синтетический датасет (100 точек, 25 стран).
- `app/main.py` — FastAPI, отдаёт `static/` (только для локального запуска).

## Импорт данных

Кнопка «Импорт JSON / CSV» в шапке. Парсинг и валидация — на клиенте.

- **JSON:** массив объектов со схемой `ip, count, country, countryCode, lat, lon,
  attacks, incidents, ports[], severity`.
- **CSV:** заголовок `ip,count,country,countryCode,lat,lon,attacks,incidents,ports,severity`;
  поле `ports` — числа через `;`.

Невалидные записи пропускаются, результат и число пропущенных строк — в уведомлении.

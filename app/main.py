"""Минимальный FastAPI-сервер: отдаёт статическую SOC-панель тепловой карты угроз.

Вся логика и данные — в браузере (см. static/index.html, static/data/threats.json).
Сервер нужен только для локального запуска; в проде статику отдаёт платформа.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Тепловая карта вредоносных IP", docs_url=None, redoc_url=None)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


def main() -> None:
    """Запустить uvicorn на 0.0.0.0:$PORT (по умолчанию 8000)."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()

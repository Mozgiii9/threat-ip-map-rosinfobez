import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI()
# Монтируем static/ в корень: index.html на "/", vendor/ и data/ — соседями.
# Так относительные пути работают одинаково локально и в проде TimeWeb (корень = /static).
app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

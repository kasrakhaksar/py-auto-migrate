from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from py_auto_migrate.dashboard.routers import home, migrate

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(home.router)
app.include_router(migrate.router)
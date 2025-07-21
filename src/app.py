# src/app.py

import logging
import asyncio
import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Korrigiertes Importieren aus dem Package 'src'
from src.scheduler import start_scheduler
from src.dependencies import get_current_user
from src.models.db import init_db
from src.routes.auth import router as auth_router
from src.routes.admin import router as admin_router

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# FastAPI-Instanz und Template-Ordner
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Router einbinden
app.include_router(auth_router)
app.include_router(admin_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

@app.get("/health", response_class=JSONResponse)
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    # .env laden, DB initialisieren, Scheduler starten
    load_dotenv()
    init_db()
    logging.info("Database initialized.")
    asyncio.create_task(start_scheduler())
    logging.info("Scheduler started.")

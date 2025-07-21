# src/app.py

import logging
import asyncio
import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from scheduler import start_scheduler
from dependencies import get_current_user
from models.db import init_db
from routes.auth import router as auth_router
from routes.admin import router as admin_router

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# FastAPI-Instanz
app = FastAPI()

# Jinja2-Templates
templates = Jinja2Templates(directory="templates")

# Router einbinden
app.include_router(auth_router)
app.include_router(admin_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(get_current_user)):
    """
    Startseite – zeigt Template 'index.html' und meldet angemeldeten User.
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

@app.get("/health")
async def health():
    """
    Health-Check für Render oder Uptime-Monitoring.
    """
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    """
    Startup-Hook: .env laden, DB initialisieren und Scheduler starten.
    """
    load_dotenv()
    # DB-Tabellen anlegen
    init_db()
    logging.info("Database initialized.")
    # Scheduler im Hintergrund starten
    asyncio.create_task(start_scheduler())
    logging.info("Scheduler task created.")

# src/app.py

import logging
import asyncio
import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
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

# Templates aus dem Ordner /app/templates laden
templates = Jinja2Templates(directory="templates")

# Alle Router einbinden
app.include_router(auth_router)
app.include_router(admin_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(get_current_user)):
    """
    Startseite mit angemeldetem User.
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

@app.get("/health", response_class=JSONResponse)
async def health():
    """
    Health-Check für Uptime-Services.
    """
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    """
    Startup: .env laden, DB initialisieren, Scheduler starten.
    """
    load_dotenv()
    init_db()
    logging.info("Database initialized.")
    # Scheduler als Hintergrund-Task starten
    asyncio.create_task(start_scheduler())
    logging.info("Scheduler started.")

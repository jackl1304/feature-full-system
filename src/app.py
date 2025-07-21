# src/app.py

import logging
import asyncio
import os

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .scheduler import start_scheduler
from .dependencies import get_current_user
from .models.db import init_db
from .routes.auth import router as auth_router
from .routes.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
    load_dotenv()
    init_db()
    logging.info("Database initialized.")
    asyncio.create_task(start_scheduler())
    logging.info("Scheduler started.")

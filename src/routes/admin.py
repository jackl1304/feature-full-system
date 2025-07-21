# src/routes/admin.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import select
from src.dependencies import get_current_admin, get_session
from src.models.user import User
from src.models.log import FetchLog
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session = Depends(get_session)):
    users = session.exec(select(User)).all()
    logs = session.exec(select(FetchLog).order_by(FetchLog.timestamp.desc())).all()
    return templates.TemplateResponse("admin.html", {
        "request": request, "users": users, "logs": logs
    })

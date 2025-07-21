# src/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlmodel import select
from src.dependencies import create_access_token, get_session
from src.models.user import User

templates = Jinja2Templates(directory="templates")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])

def hash_pw(pw: str) -> str:
    return pwd_ctx.hash(pw)

def verify_pw(pw: str, hsh: str) -> bool:
    return pwd_ctx.verify(pw, hsh)

@router.get("/register", response_class=HTMLResponse)
async def form_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(email: str = Form(...), password: str = Form(...), session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == email)).first()
    if exists:
        raise HTTPException(400, "E-Mail bereits registriert")
    user = User(email=email, password_hash=hash_pw(password))
    session.add(user); session.commit(); session.refresh(user)
    return RedirectResponse("/auth/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
async def form_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/token")
async def login_for_token(email: str = Form(...), password: str = Form(...), session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_pw(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Falsche Anmeldedaten")
    token = create_access_token({"sub": str(user.id)})
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie("Authorization", f"Bearer {token}", httponly=True)
    return resp

@router.get("/logout")
async def logout():
    resp = RedirectResponse("/auth/login", status_code=302)
    resp.delete_cookie("Authorization")
    return resp

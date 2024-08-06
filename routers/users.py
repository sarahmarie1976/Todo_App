import sys
sys.path.append("..")

from starlette import status 
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, verify_password, get_password_hash

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users",
    tags=['users'],
    responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str

@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user})

@router.post("/edit-password", response_class=HTMLResponse)
async def edit_user_post(request: Request, username: str = Form(...), original_password: str = Form(...),
                         new_password: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    db_user = db.query(models.Users).filter(models.Users.id == user["id"]).first()
    
    if db_user.username != username or not verify_password(original_password, db_user.hashed_password):
        msg = "Invalid username or password"
        return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": db_user, "msg": msg, "msg_type": "danger"})
    
    db_user.hashed_password = get_password_hash(new_password)
    
    db.commit()
    msg = "Password updated"
    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": db_user, "msg": msg, "msg_type": "success"})

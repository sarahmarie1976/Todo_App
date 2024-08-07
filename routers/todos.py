import sys
sys.path.append("..")
from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class TodoForm(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=3, max_length=1000)
    priority: int = Field(..., ge=1, le=5)

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        priority: int = Form(...)
    ) -> "TodoForm":
        return cls(title=title, description=description, priority=priority)

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, form_data: TodoForm = Depends(TodoForm.as_form), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = models.Todos()
    todo_model.title = form_data.title
    todo_model.description = form_data.description
    todo_model.priority = form_data.priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, form_data: TodoForm = Depends(TodoForm.as_form), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo_model.title = form_data.title
    todo_model.description = form_data.description
    todo_model.priority = form_data.priority
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}")
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo.complete = not todo.complete
    db.add(todo)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

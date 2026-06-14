from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)
templates = Jinja2Templates(directory="TODOapp/templates")


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


async def get_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if token is None:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    user = await get_user_from_cookie(request)

    if user is None:
        return redirect_to_login()

    todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

    return templates.TemplateResponse(request, "todo.html", {"todos": todos, "user": user})


@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    user = await get_user_from_cookie(request)

    if user is None:
        return redirect_to_login()

    return templates.TemplateResponse(request, "add-todo.html", {"user": user})


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    user = await get_user_from_cookie(request)

    if user is None:
        return redirect_to_login()

    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()

    if todo is None:
        return redirect_to_login()

    return templates.TemplateResponse(request, "edit-todo.html", {"todo": todo, "user": user})


### Endpoints ###

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(todo_id: Annotated[int, Path(gt=0)], user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))

    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    todo_id: Annotated[int, Path(gt=0)],
    todo_request: TodoRequest,
    user: user_dependency,
    db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: Annotated[int, Path(gt=0)], user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo_model)
    db.commit()

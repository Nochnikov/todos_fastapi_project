from fastapi import APIRouter, Depends, Path, HTTPException, Request
from pydantic import BaseModel, Field
from starlette import status

from .. import models
from ..models import Todos
from ..database import SessionLocal, engine
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from  fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=["Todos"],
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

templates = Jinja2Templates(directory="TodoApp/templates")

class Todo(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/test")
async def test(request: Request):

    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).filter(Todos.owner_id == user.get("user_id")).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(todo_id == Todos.id).filter(Todos.owner_id == user.get('user_id')).first()

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency,
                      todo: Todo):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    todo_model = Todos(**todo.model_dump(), owner_id=user.get('user_id'))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependency,
        db: db_dependency,
        todo: Todo,
        todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        user: user_dependency,
        db: db_dependency,
        todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).delete()
    db.commit()

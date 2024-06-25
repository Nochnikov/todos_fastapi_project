from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status

from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_bd():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_bd)]


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post('/auth/register', status_code=status.HTTP_201_CREATED)
async def create_user(user_create: CreateUser, db: db_dependency):
    created_user = Users(
        username=user_create.username,
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role=user_create.role,
        hashed_password=bcrypt_context.hash(user_create.password),
        is_active=True
    )
    db.add(created_user)
    db.commit()



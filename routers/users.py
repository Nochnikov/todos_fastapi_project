
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from ..models import Users
from ..database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_current_user
from .auth import bcrypt_context
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix="/users",
    tags=['users']
)


@router.get('/me', status_code=200)
async def get_current_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    return db.query(Users).filter(Users.id == user.get('user_id')).first()

class PasswordReset(BaseModel):
    old_password: str
    new_password: str

@router.patch('/update_password', status_code=204)
async def update_password(passwords: PasswordReset, db: db_dependency, user: user_dependency):

    new_password = passwords.new_password
    old_password = passwords.old_password

    model = db.query(Users).filter(Users.id == user.get('user_id')).first()

    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not bcrypt_context.verify(old_password, model.hashed_password):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="That's not your current password")

    if bcrypt_context.verify(new_password, model.hashed_password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Passwords must not match')


    model.hashed_password = bcrypt_context.hash(new_password)

    db.add(model)
    db.commit()


class PhoneRequest(BaseModel):
    phone_number: str

@router.patch('/phone/update', status_code=204)
async def update_phone(request: PhoneRequest, db: db_dependency, user: user_dependency):

    new_phone = request.phone_number


    model = db.query(Users).filter(Users.id == user.get('user_id')).first()

    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    elif new_phone is None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Phone number cannot be null')

    model.phone_number = new_phone

    db.add(model)
    db.commit()





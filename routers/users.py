
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from starlette import status
from models import Users
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_current_user
from .auth import oauth2_bearer, SECRET_KEY, ALGORITHM
from .auth import bcrypt_context, CreateUser
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


@router.get('/me')
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('id')
        token_type = payload.get('type')


        if user_id is None or token_type != "ACCESS":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user_data = db.query(Users).filter_by(id=user_id).first()
        return user_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.patch('/update_password')
async def update_password(password: str, db: db_dependency, user: user_dependency):

    model = db.query(Users).filter(Users.id == user.get('user_id')).first()

    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if bcrypt_context.verify(password, model.hashed_password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Passwords must not match')

    model.hashed_password = bcrypt_context.encrypt(password)

    db.add(model)
    db.commit()








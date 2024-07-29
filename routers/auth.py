from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from ..models import Users
from passlib.context import CryptContext
from ..database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer
from jose import jwt, JWTError

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(http_bearer)]
)

SECRET_KEY = 'f1752dc32e3fb604d66332c5148cbf9610dffeb86a9330c9a89fff2d4673b81d'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta = timedelta(minutes=20)):

    encode = {"sub": username, "id": user_id, 'type': 'ACCESS', 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, 'type': 'REFRESH', 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        token_type = payload.get('type')

        if token_type != 'REFRESH':
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Token is invalid")
        elif username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token payload is missing required"
                                                                                "fields")

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        token_type: str = payload.get("type")
        user_role: str = payload.get("role")

        if token_type != "ACCESS":
            raise HTTPException(status_code=401, detail="Invalid token type")
        elif username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        return {'username': username, 'user_id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")


class CreateUser(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str

@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(user_create: CreateUser, db: db_dependency):
    created_user = Users(
        username=user_create.username,
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        role=user_create.role,
        hashed_password=bcrypt_context.hash(user_create.password),
        is_active=True,
        phone_number=user_create.phone_number,
    )
    db.add(created_user)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")


    access_token = create_access_token(user.username, user.id, user.role)
    refresh_token = create_refresh_token(user.username, user.id, user.role, timedelta(hours=24))

    return {"access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"}

@router.post("/refresh", response_model=Token, response_model_exclude_none=True)
async def refresh_access_token(refresh_token: Annotated[str, Depends(oauth2_bearer)]):
    payload = verify_token(refresh_token)

    username = payload.get("sub")
    user_id = payload.get("id")
    user_role = payload.get("role")

    access_token = create_access_token(username=username, user_id=user_id, user_role=user_role, expires_delta=timedelta(hours=24))
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


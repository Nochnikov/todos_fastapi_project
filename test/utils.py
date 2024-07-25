from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from fastapi.testclient import TestClient
import pytest

from ..main import app
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URI = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "TestUser", "user_id": 1, "user_role": 'admin'}


client = TestClient(app)


@pytest.fixture()
def test_user():
    user = Users(
        username="TestUser",
        email="<EMAILasasasas>",
        first_name="TestFirst",
        last_name="TestLast",
        hashed_password=bcrypt_context.hash("<PASSWORD123>"),
        role='admin',
        phone_number="+55555555555"
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Test1",
        description="Test2",
        priority=1,
        complete=False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.commit()


from .utils import *
from ..routers.auth import authenticate_user, get_db, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi.exceptions import HTTPException

app.dependency_overrides[get_db] = override_get_db



def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "<PASSWORD123>", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_uer =  authenticate_user("test_user.username", "<PASSWORD>", db)
    assert non_existent_uer is False

    wrong_password_user = authenticate_user(test_user.username, "wrongpass", db)
    assert wrong_password_user is False


def test_create_access_token():
    username = 'test_user'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)


    token = create_access_token(username, user_id, role, expires_delta)

    decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decode_token['sub'] == username
    assert decode_token['id'] == user_id
    assert decode_token['role'] == role
@pytest.mark.asyncio
async def test_get_current_user_valid_token():

    encode = {"sub": "test_user", "id": 1, "role": "admin", "type": "ACCESS"}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    user = await get_current_user(token)

    assert user == {"username": "test_user", "user_id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"sub": "test_user", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException) as excinf:
        await get_current_user(token)

    assert excinf.value.status_code == 401
    assert excinf.value.detail == 'Invalid token type'







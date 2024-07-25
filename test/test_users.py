from sqlalchemy.testing.pickleable import User

from .utils import *
from ..routers.users import get_current_user, get_db



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user



def test_return_user(test_user):
    response = client.get("/users/me")
    assert response.status_code == 200
    assert response.json()['username'] == 'TestUser'
    assert response.json()['email'] == '<EMAILasasasas>'
    assert response.json()['first_name'] == 'TestFirst'
    assert response.json()['last_name'] == 'TestLast'


def test_update_password(test_user):
    response = client.patch("/users/update_password", json={"old_password": "PASSWORD123", "new_password": "test123"})
    assert response.status_code == 204
    """
    update here some problems
    """








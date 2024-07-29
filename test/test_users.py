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
    response = client.patch("/users/update_password", json={"old_password": "<PASSWORD123>", "new_password": "test123"})
    assert response.status_code == 204

def test_update_password_invalid(test_user):
    response = client.patch("/users/update_password", json={"old_password": "wrong_password",
                                                            "new_password": "<PASSWORD>"})
    assert response.status_code == 405
    assert response.json() == {'detail': "That's not your current password"}


def test_update_phone_number(test_user):

    response = client.patch("/users/phone/update",  json={"phone_number": "+1234567890"})

    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert model.phone_number == "+1234567890"










from starlette import status
from .utils import override_get_db, override_get_current_user, client, TestingSessionLocal, test_todo
from ..main import app
from ..routers.todos import get_db
from ..routers.todos import get_current_user
from ..models import Todos


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get('/todos/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Test1', 'description': 'Test2', 'priority': 1, 'complete': False,
                                'owner_id': 1, "id": 1}]

def test_read_one_authenticated(test_todo):
    response = client.get('/todos/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Test1', 'description': 'Test2', 'priority': 1, 'complete': False,
                                'owner_id': 1, "id": 1}


def test_read_one_authenticated_fail(test_todo):
    response = client.get('/todos/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found'}

def test_create_todo(test_todo):
    request_data = {'title': 'Test_create',
                    'description': 'Test_create_123',
                    'priority': 5,
                    'complete': False,
                    'owner_id': 1}

    response = client.post('/todos/todo', json=request_data)

    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(2 == Todos.id).first()
    assert model.title == request_data.get('title')


def test_update_todo(test_todo):
    request_data = {'title': 'Test_create_update',
                    'description': 'Test_create_1234',
                    'priority': 5,
                    'complete': False,
                    'owner_id': 1}

    response = client.put('/todos/todo/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT


    db = TestingSessionLocal()
    model = db.query(Todos).filter(1 == Todos.id).first()
    assert model.title == request_data.get('title')



def test_update_todo_fail(test_todo):
    request_data = {'title': 'Test_create_update',
                    'description': 'Test_create_1234',
                    'priority': 5,
                    'complete': False,
                    'owner_id': 1}

    response = client.put('/todos/todo/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')

    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_fail(test_todo):
    response = client.delete('/todos/todo/741')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}





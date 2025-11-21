# TodoApp/test/test_todos.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from fastapi import status

from ..database import Base
from ..main import app
from ..routers.todos import get_db
from ..routers.auth import get_current_user
from ..models import Todos

# -------------------- Test Database --------------------
SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create tables
Base.metadata.create_all(bind=engine)

# -------------------- Dependency Overrides --------------------
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'aliereza', 'id': 1, 'user_role': 'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

# -------------------- Fixtures --------------------
@pytest.fixture
def test_todo():
    db = TestingSessionLocal()
    todo = Todos(
        title='learn to code',
        description='need to learn everyday!',
        priority=5,
        complete=False,
        owner_id=1
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    yield todo  # Provide the todo to the test

    # Cleanup after test
    db.query(Todos).delete()
    db.commit()
    db.close()

# -------------------- Tests --------------------
def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'id': test_todo.id,
            'title': test_todo.title,
            'description': test_todo.description,
            'priority': test_todo.priority,
            'complete': test_todo.complete,
            'owner_id': test_todo.owner_id
        }
    ]

def test_read_one_authenticated(test_todo):
    response = client.get(f'/todo/{test_todo.id}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': test_todo.id,
        'title': test_todo.title,
        'description': test_todo.description,
        'priority': test_todo.priority,
        'complete': test_todo.complete,
        'owner_id': test_todo.owner_id
    }



def test_read_one_authenticated_not_found():
    response = client.get('/todo/999')
    assert response.status_code == 200
    assert response.json() == {'detail': 'Todo not found'}
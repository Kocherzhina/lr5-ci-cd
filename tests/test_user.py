import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Исходные данные (Master Data)
MASTER_USERS = [
    {'id': 1, 'name': 'Ivan Ivanov', 'email': 'i.i.ivanov@mail.com'},
    {'id': 2, 'name': 'Pyotr Petrov', 'email': 'p.p.petrov@mail.com'}
]

# ФИКСТУРА: выполняется перед КАЖДЫМ тестом
@pytest.fixture(autouse=True)
def db_state():
    # Импортируем функции БД
    from src.fake_db.database import _users, _next_id, _USERS_DATA
    
    # Принудительно сбрасываем глобальные переменные в БД к исходному состоянию
    _users.clear()
    _users.extend(_USERS_DATA.copy())
    global _next_id
    _next_id = 3

def test_get_existed_user():
    response = client.get("/api/v1/user", params={'email': MASTER_USERS[0]['email']})
    assert response.status_code == 200
    assert response.json()['id'] == 1

def test_get_unexisted_user():
    response = client.get("/api/v1/user", params={'email': 'ghost@mail.com'})
    assert response.status_code == 404

def test_create_user_with_valid_email():
    response = client.post("/api/v1/user", json={"name": "Sidor", "email": "sidor@mail.com"})
    assert response.status_code == 201
    assert response.json() == 3

def test_create_user_with_invalid_email():
    response = client.post("/api/v1/user", json={"name": "Dup", 'email': MASTER_USERS[0]['email']})
    assert response.status_code == 409

def test_delete_user():
    # Удаляем второго пользователя (Петра)
    response = client.delete("/api/v1/user", params={'email': MASTER_USERS[1]['email']})
    assert response.status_code == 204
    
    # Проверяем, что он удален
    check = client.get("/api/v1/user", params={'email': MASTER_USERS[1]['email']})
    assert check.status_code == 404

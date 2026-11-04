from fastapi.testclient import TestClient
from src.main import app  # Импортируем реальное приложение

client = TestClient(app)

users = [
    {'id': 1, 'name': 'Ivan Ivanov', 'email': 'i.i.ivanov@mail.com'},
    {'id': 2, 'name': 'Pyotr Petrov', 'email': 'p.p.petrov@mail.com'}
]

def test_get_existed_user():
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200

def test_get_unexisted_user():
    response = client.get("/api/v1/user", params={'email': 'ghost@mail.com'})
    assert response.status_code == 404

def test_create_user_with_valid_email():
    response = client.post("/api/v1/user", json={"name": "Sidor", "email": "sidor@mail.com"})
    assert response.status_code == 201

def test_create_user_with_invalid_email():
    response = client.post("/api/v1/user", json={"name": "Dup", 'email': users[0]['email']})
    assert response.status_code == 409

def test_delete_user():
    response = client.delete("/api/v1/user", params={'email': users[1]['email']})
    assert response.status_code == 204
    check = client.get("/api/v1/user", params={'email': users[1]['email']})
    assert check.status_code == 404

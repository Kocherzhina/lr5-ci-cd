import pytest
from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.testclient import TestClient

MASTER_USERS = [
    {'id': 1, 'name': 'Ivan Ivanov', 'email': 'i.i.ivanov@mail.com'},
    {'id': 2, 'name': 'Pyotr Petrov', 'email': 'p.p.petrov@mail.com'}
]

# --- База данных (внутри теста) ---
_fake_storage = MASTER_USERS.copy()
_next_id = 3

def reset_db():
    global _fake_storage, _next_id
    _fake_storage = MASTER_USERS.copy()
    _next_id = 3

def get_user_by_email(email: str):
    for user in _fake_storage:
        if user['email'] == email:
            return user
    return None

def create_user(name: str, email: str):
    global _next_id
    if get_user_by_email(email):
        return None
    user = {'id': _next_id, 'name': name, 'email': email}
    _fake_storage.append(user)
    _next_id += 1
    return user

def delete_user_by_email(email: str):
    global _fake_storage
    for user in _fake_storage:
        if user['email'] == email:
            _fake_storage.remove(user)
            return True
    return False

# --- Роутер ---
user_router = APIRouter()

@user_router.get("", status_code=status.HTTP_200_OK)
def get_user(email: str):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    return user

@user_router.post("", status_code=status.HTTP_201_CREATED)
def create_user_endpoint(data: dict):
    name, email = data.get("name"), data.get("email")
    if get_user_by_email(email):
        raise HTTPException(status_code=409, detail="User with this email already exists")
    return create_user(name, email)['id']

@user_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(email: str):
    if not delete_user_by_email(email):
        raise HTTPException(status_code=404, detail="Not Found")
    return None

# --- Сборка ---
app = FastAPI()
app.include_router(user_router, prefix="/api/v1/user")
client = TestClient(app)

# --- ДИАГНОСТИКА: Печатаем все маршруты ---
@pytest.fixture(autouse=True)
def run_around_tests():
    reset_db()
    # ЭТА СТРОКА ВЫВЕДЕТ АДРЕСА В ЛОГИ GITHUB
    print("\n--- REGISTERED ROUTES ---")
    for route in app.routes:
        # Проверяем, есть ли у маршрута path (чтобы не упасть на Starlette ошибки)
        if hasattr(route, 'path'):
            methods = [m for m in route.methods if not m.startswith('HEAD')]
            print(f"Path: {route.path} | Methods: {methods}")
    print("--- END ROUTES ---\n")
    yield

# --- Тесты (пути "" так как префикс на роутере) ---
def test_get_existed_user():
    response = client.get("", params={'email': MASTER_USERS[0]['email']})
    assert response.status_code == 200

def test_get_unexisted_user():
    response = client.get("", params={'email': 'ghost@mail.com'})
    assert response.status_code == 404

def test_create_user_with_valid_email():
    response = client.post("", json={"name": "Sidor", "email": "sidor@mail.com"})
    assert response.status_code == 201

def test_create_user_with_invalid_email():
    response = client.post("", json={"name": "Dup", 'email': MASTER_USERS[0]['email']})
    assert response.status_code == 409

def test_delete_user():
    response = client.delete("", params={'email': MASTER_USERS[1]['email']})
    assert response.status_code == 204

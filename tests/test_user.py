from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

# --- ДАННЫЕ ---
users_data = [
    {"id": 1, "name": "Ivan", "email": "ivan@mail.com"},
    {"id": 2, "name": "Pyotr", "email": "petr@mail.com"}
]
db = users_data.copy()

def find_user(email):
    for u in db:
        if u["email"] == email:
            return u
    return None

# --- ПРИЛОЖЕНИЕ ---
app = FastAPI()

@app.get("/api/v1/user")
def get_user(email: str):
    user = find_user(email)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    return user

# ФИКС: Возвращаем объект {"id": 3}, а не просто 3
@app.post("/api/v1/user", status_code=201)
def create_user(name: str, email: str):
    if find_user(email):
        raise HTTPException(status_code=409, detail="Already exists")
    
    new_id = len(db) + 1
    db.append({"id": new_id, "name": name, "email": email})
    # Возвращаем словарь
    return {"id": new_id}

@app.delete("/api/v1/user", status_code=204)
def delete_user(email: str):
    global db
    for u in db:
        if u["email"] == email:
            db = [x for x in db if x["email"] != email]
            return 
    raise HTTPException(status_code=404, detail="Not Found")

client = TestClient(app)

# --- ТЕСТЫ ---
def test_get_existed_user():
    response = client.get("/api/v1/user", params={"email": "ivan@mail.com"})
    assert response.status_code == 200

def test_get_unexisted_user():
    response = client.get("/api/v1/user", params={"email": "ghost@mail.com"})
    assert response.status_code == 404

def test_create_user():
    response = client.post("/api/v1/user", json={"name": "Sidor", "email": "sidor@mail.com"})
    assert response.status_code == 201
    # Проверяем словарь
    assert response.json() == {"id": 3}

def test_create_duplicate():
    response = client.post("/api/v1/user", json={"name": "X", "email": "ivan@mail.com"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Already exists"

def test_delete_user():
    response = client.delete("/api/v1/user", params={"email": "petr@mail.com"})
    assert response.status_code == 204
    check = client.get("/api/v1/user", params={"email": "petr@mail.com"})
    assert check.status_code == 404

# check_routes.py
from tests.test_user import app  # Импортируем наше "чистое" приложение из теста

print("=== Зарегистрированные маршруты ===")
for route in app.routes:
    print(f"Path: {route.path} | Methods: {route.methods}")
print("==================================")

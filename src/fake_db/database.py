# src/fake_db/database.py
_USERS_DATA = [
    {'id': 1, 'name': 'Ivan Ivanov', 'email': 'i.i.ivanov@mail.com'},
    {'id': 2, 'name': 'Pyotr Petrov', 'email': 'p.p.petrov@mail.com'}
]

_users = _USERS_DATA.copy()
_next_id = 3

def reset_db():
    global _users, _next_id
    _users = _USERS_DATA.copy()
    _next_id = 3

def get_user_by_email(email: str):
    print(f"[DEBUG] DB: Searching for email={email}. Current DB state: {_users}")
    for user in _users:
        if user['email'] == email:
            return user
    return None

def create_user(name: str, email: str):
    global _next_id
    if get_user_by_email(email) is not None:
        return None
    user = {'id': _next_id, 'name': name, 'email': email}
    _users.append(user)
    _next_id += 1
    return user

def delete_user_by_email(email: str):
    global _users
    for user in _users:
        if user['email'] == email:
            _users.remove(user)
            return True
    return False

db = type('DB', (), {
    'get_user_by_email': staticmethod(get_user_by_email),
    'create_user': staticmethod(create_user),
    'delete_user_by_email': staticmethod(delete_user_by_email)
})()

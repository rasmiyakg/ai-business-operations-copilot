import hashlib

USERS = {
    "admin": {
        "password": "admin123",
        "role": "Admin"
    },
    "staff": {
        "password": "staff123",
        "role": "Staff"
    }
}


def authenticate(username, password):

    if username in USERS:
        if USERS[username]["password"] == password:
            return USERS[username]["role"]

    return None
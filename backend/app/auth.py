import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .models import User
import json
import os

SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

USERS_FILE = "users.json"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def upsert_user(user: User):
    users = load_users()
    users[user.username] = user.dict()
    save_users(users)

def authenticate_user(username: str, password: str) -> User:
    users = load_users()
    user_data = users.get(username)
    if not user_data:
        return None
    # NOTE: For this multi-user fix, password check is only used for 2FA step.
    if user_data["password"] != password:
        return None
    return User(**user_data)

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    users = load_users()
    user_data = users.get(username)
    if user_data is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user_data)
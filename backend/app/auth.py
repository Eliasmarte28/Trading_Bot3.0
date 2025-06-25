from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .models import User
import jwt
from datetime import datetime, timedelta

users_db = {
    "admin": {"username": "admin", "password": "admin", "api_key": "", "use_demo": True},
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "YOUR_SECRET_KEY_HERE"

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or user["password"] != password:
        return None
    return User(**user)

def create_access_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=12)
    to_encode = {"sub": username, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        user = users_db.get(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid user")
        return User(**user)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")
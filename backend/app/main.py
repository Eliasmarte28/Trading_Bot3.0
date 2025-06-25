from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .auth import authenticate_user, create_access_token, get_current_user
from .capitalcom_api import CapitalComAPI
from .models import User
from .config import settings
from .market_scan import generate_daily_report
from .scheduler import start_scheduler
import os
import json

app = FastAPI(title="Capital.com Trading Bot API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str
    api_key: str
    api_key_password: str
    use_demo: bool = True

class Login2FARequest(LoginRequest):
    otp: str

@app.post("/login")
def login(req: LoginRequest):
    # First, verify user locally (if you have a local User DB)
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Attempt Capital.com login (without OTP)
    api = CapitalComAPI(
        email=req.username,
        password=req.password,
        api_key=req.api_key,
        api_key_password=req.api_key_password,
        demo=req.use_demo,
    )
    login_result = api.login()

    if login_result.get("2fa_required"):
        # Prompt frontend to ask for OTP
        user.api_key = req.api_key
        user.api_key_password = req.api_key_password
        user.use_demo = req.use_demo
        user.temp_cc_login_data = api.get_login_context()  # Save for 2FA
        return {"2fa_required": True}
    elif not login_result.get("success"):
        raise HTTPException(status_code=401, detail=login_result.get("error", "Login failed. Check credentials and API key."))
    else:
        # Success: generate token and store Capital.com session/token
        token = create_access_token(user.username)
        user.api_key = req.api_key
        user.api_key_password = req.api_key_password
        user.use_demo = req.use_demo
        user.cc_session_token = login_result["session_token"]
        if user.username == "admin":
            start_scheduler(user.api_key, user.use_demo)
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }

@app.post("/login-2fa")
def login_2fa(req: Login2FARequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Retrieve context from previous login step (should be stored securely)
    login_context = getattr(user, "temp_cc_login_data", None)
    if not login_context:
        raise HTTPException(status_code=400, detail="2FA context missing. Please login again.")

    api = CapitalComAPI(
        email=req.username,
        password=req.password,
        api_key=req.api_key,
        api_key_password=req.api_key_password,
        demo=req.use_demo,
        login_context=login_context
    )
    login_result = api.login(otp=req.otp)

    if not login_result.get("success"):
        raise HTTPException(status_code=401, detail=login_result.get("error", "2FA failed."))
    else:
        token = create_access_token(user.username)
        user.cc_session_token = login_result["session_token"]
        # Clean up temp context
        user.temp_cc_login_data = None
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }

@app.get("/account")
def get_account(user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        session_token=user.cc_session_token,
        demo=user.use_demo
    )
    return api.get_account_info()

class TradeRequest(BaseModel):
    symbol: str
    side: str  # "BUY" or "SELL"
    amount: float
    take_profit: float = None
    stop_loss: float = None

@app.post("/trade")
def place_trade(req: TradeRequest, user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        session_token=user.cc_session_token,
        demo=user.use_demo
    )
    return api.place_order(req.symbol, req.side, req.amount, req.take_profit, req.stop_loss)

@app.get("/trades")
def get_trades(user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        session_token=user.cc_session_token,
        demo=user.use_demo
    )
    return api.get_trades()

@app.get("/daily-report")
def get_daily_report():
    if not os.path.exists(settings.daily_report_file):
        generate_daily_report("demo-api-key", demo=True)
    with open(settings.daily_report_file) as f:
        return json.load(f)
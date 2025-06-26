from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# CORS configuration - production: restrict as much as possible!
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

@app.get("/", tags=["General"])
def read_root():
    """
    Root endpoint to verify API is running.
    """
    return {"message": "Hello, FastAPI is running! See /docs for API documentation."}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """
    Favicon endpoint to prevent 404s in browser/devtools.
    """
    return JSONResponse(status_code=204, content=None)

# ------------------- Models -------------------

class LoginRequest(BaseModel):
    username: str
    password: str
    api_key: str
    api_key_password: str
    use_demo: bool = True

class Login2FARequest(LoginRequest):
    otp: str

class TradeRequest(BaseModel):
    symbol: str
    side: str  # "BUY" or "SELL"
    amount: float
    take_profit: float = None
    stop_loss: float = None

# ------------------- Endpoints -------------------

@app.post("/login")
def login(req: LoginRequest):
    """
    Login endpoint. Handles real authentication with Capital.com.
    """
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    api = CapitalComAPI(
        email=req.username,
        password=req.password,
        api_key=req.api_key,
        api_key_password=req.api_key_password,
        demo=req.use_demo,
    )
    login_result = api.login()
    if login_result.get("2fa_required"):
        # Save context for 2FA
        user.api_key = req.api_key
        user.api_key_password = req.api_key_password
        user.use_demo = req.use_demo
        user.temp_cc_login_data = api.get_login_context()
        return {"2fa_required": True}
    elif not login_result.get("success"):
        raise HTTPException(status_code=401, detail=login_result.get("error", "Login failed. Check credentials and API key."))
    else:
        # Store session token securely for later use
        session_token = login_result["session_token"]
        token = create_access_token(user.username)
        user.api_key = req.api_key
        user.api_key_password = req.api_key_password
        user.use_demo = req.use_demo
        user.cc_session_token = session_token
        # Only admin starts scheduler
        if user.username == "admin":
            start_scheduler(user.api_key, user.use_demo)
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }

@app.post("/login-2fa")
def login_2fa(req: Login2FARequest):
    """
    Login endpoint for 2FA. Handles real authentication with Capital.com using OTP.
    """
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

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
        # Store real session token
        session_token = login_result["session_token"]
        token = create_access_token(user.username)
        user.cc_session_token = session_token
        user.temp_cc_login_data = None
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }

@app.get("/account")
def get_account(user: User = Depends(get_current_user)):
    """
    Get account info from Capital.com. Uses session token obtained at login.
    """
    api = CapitalComAPI(
        email=user.username,
        password=user.password,
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        demo=user.use_demo
    )
    # Set the real session token for authenticated requests
    api.session_token = user.cc_session_token
    return api.get_account_info()

@app.post("/trade")
def place_trade(req: TradeRequest, user: User = Depends(get_current_user)):
    """
    Place a trade at Capital.com. Requires authentication and a valid session token.
    """
    api = CapitalComAPI(
        email=user.username,
        password=user.password,
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        demo=user.use_demo
    )
    api.session_token = user.cc_session_token
    return api.place_trade(req.symbol, req.side, req.amount, req.take_profit, req.stop_loss)

@app.get("/trades")
def get_trades(user: User = Depends(get_current_user)):
    """
    Get list of trades from Capital.com.
    """
    api = CapitalComAPI(
        email=user.username,
        password=user.password,
        api_key=user.api_key,
        api_key_password=user.api_key_password,
        demo=user.use_demo
    )
    api.session_token = user.cc_session_token
    return api.get_trades()

@app.get("/daily-report")
def get_daily_report():
    """
    Get the latest daily report. In production, ensure this is generated from real data.
    """
    if not os.path.exists(settings.daily_report_file):
        generate_daily_report("demo-api-key", demo=True)
    with open(settings.daily_report_file) as f:
        return json.load(f)
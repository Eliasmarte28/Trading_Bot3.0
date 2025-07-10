from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .auth import authenticate_user, create_access_token, upsert_user, get_current_user, get_password_hash
from .models import User
from .capitalcom_api import CapitalComAPI
from .schemas import SignupRequest, LoginRequest, Login2FARequest, TradeRequest
from .daily_report import router as daily_report_router
from .risk_settings import router as risk_settings_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup")
def signup(req: SignupRequest):
    user = User(
        username=req.username,
        password=get_password_hash(req.password),
        api_key=req.api_key,
        api_key_password=req.api_key_password,
        use_demo=req.use_demo,
    )
    upsert_user(user)
    return {"msg": "User created"}

@app.post("/login")
def login(req: LoginRequest):
    print("Login request data:", req.dict())
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print("Sending to CapitalComAPI:", {
        "identifier": req.username,
        "password": req.password,
        "api_key": req.api_key,
        "demo": req.use_demo,
    })
    api = CapitalComAPI(
        identifier=req.username,
        password=req.password,
        api_key=req.api_key,
        demo=req.use_demo,
    )
    login_result = api.login()
    print("CapitalComAPI login_result:", login_result)
    if login_result.get("2fa_required"):
        user.api_key = req.api_key
        user.api_key_password = req.api_key_password
        user.use_demo = req.use_demo
        user.temp_cc_login_data = api.get_login_context()
        upsert_user(user)
        return {"2fa_required": True}
    elif not login_result.get("success"):
        raise HTTPException(
            status_code=401,
            detail=login_result.get("error", "Login failed. Make sure your Capital.com email and API key are correct.")
        )
    else:
        account_info = {
            "accountType": login_result.get("accountType"),
            "accountInfo": login_result.get("accountInfo"),
            "currencyIsoCode": login_result.get("currencyIsoCode"),
            "currencySymbol": login_result.get("currencySymbol"),
            "currentAccountId": login_result.get("currentAccountId"),
            "streamingHost": login_result.get("streamingHost"),
            "accounts": login_result.get("accounts"),
            "clientId": login_result.get("clientId"),
            "timezoneOffset": login_result.get("timezoneOffset"),
            "hasActiveDemoAccounts": login_result.get("hasActiveDemoAccounts"),
            "hasActiveLiveAccounts": login_result.get("hasActiveLiveAccounts"),
            "trailingStopsEnabled": login_result.get("trailingStopsEnabled"),
        }
        token = create_access_token(user.username)
        user.api_key = req.api_key
        user.api_key_password = req.api_key_password
        user.use_demo = req.use_demo
        user.account_info = account_info
        upsert_user(user)
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
    login_context = getattr(user, "temp_cc_login_data", None)
    if not login_context:
        raise HTTPException(status_code=400, detail="2FA context missing. Please login again.")
    api = CapitalComAPI(
        identifier=req.username,
        password=req.password,
        api_key=req.api_key,
        demo=req.use_demo,
        login_context=login_context
    )
    login_result = api.login(otp=req.otp)
    if not login_result.get("success"):
        raise HTTPException(status_code=401, detail=login_result.get("error", "2FA failed."))
    else:
        account_info = {
            "accountType": login_result.get("accountType"),
            "accountInfo": login_result.get("accountInfo"),
            "currencyIsoCode": login_result.get("currencyIsoCode"),
            "currencySymbol": login_result.get("currencySymbol"),
            "currentAccountId": login_result.get("currentAccountId"),
            "streamingHost": login_result.get("streamingHost"),
            "accounts": login_result.get("accounts"),
            "clientId": login_result.get("clientId"),
            "timezoneOffset": login_result.get("timezoneOffset"),
            "hasActiveDemoAccounts": login_result.get("hasActiveDemoAccounts"),
            "hasActiveLiveAccounts": login_result.get("hasActiveLiveAccounts"),
            "trailingStopsEnabled": login_result.get("trailingStopsEnabled"),
        }
        user.account_info = account_info
        user.temp_cc_login_data = None
        upsert_user(user)
        token = create_access_token(user.username)
        return {
            "access_token": token,
            "token_type": "bearer",
            "username": user.username
        }

@app.get("/account")
def get_account(user: User = Depends(get_current_user)):
    if user.account_info:
        return user.account_info
    else:
        raise HTTPException(status_code=404, detail="No account info available. Please log in again.")

@app.post("/trade")
def place_trade(req: TradeRequest, user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        identifier=user.username,
        password=user.password,
        api_key=user.api_key,
        demo=user.use_demo
    )
    return api.place_trade(req.symbol, req.side, req.amount, req.take_profit, req.stop_loss)

@app.get("/trades")
def get_trades(user: User = Depends(get_current_user)):
    api = CapitalComAPI(
        identifier=user.username,
        password=user.password,
        api_key=user.api_key,
        demo=user.use_demo
    )
    return api.get_trades()

app.include_router(daily_report_router)
app.include_router(risk_settings_router)
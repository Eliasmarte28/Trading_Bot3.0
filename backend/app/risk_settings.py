from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
import json
import os

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for demonstration (replace with a proper database in production)
RISK_SETTINGS_FILE = "risk_settings.json"

class RiskSettings(BaseModel):
    concurrentTrades: int = 1
    riskPerTrade: float = 2
    maxDailyLoss: float = 20
    profitTarget: float = 50
    leverage: int = 10

def load_all_settings():
    if os.path.exists(RISK_SETTINGS_FILE):
        with open(RISK_SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_all_settings(data):
    with open(RISK_SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def get_user_id_from_token(token: str):
    # Replace with your real authentication logic.
    # For now, use token as username for demo.
    return token

@router.get("/risk-settings")
async def get_risk_settings(token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    all_settings = load_all_settings()
    return all_settings.get(user_id, RiskSettings().dict())

@router.post("/risk-settings")
async def set_risk_settings(settings: RiskSettings, token: str = Depends(oauth2_scheme)):
    user_id = get_user_id_from_token(token)
    all_settings = load_all_settings()
    all_settings[user_id] = settings.dict()
    save_all_settings(all_settings)
    return settings.dict()
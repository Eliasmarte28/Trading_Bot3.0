from pydantic import BaseModel
from typing import Optional

class SignupRequest(BaseModel):
    username: str
    password: str
    api_key: str
    api_key_password: str
    use_demo: bool

class LoginRequest(BaseModel):
    username: str
    password: str
    api_key: str
    api_key_password: str
    use_demo: bool

class Login2FARequest(BaseModel):
    username: str
    password: str
    api_key: str
    api_key_password: str
    use_demo: bool
    otp: str

class TradeRequest(BaseModel):
    symbol: str
    side: str
    amount: float
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
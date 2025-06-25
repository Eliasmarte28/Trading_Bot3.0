from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "YOUR_SECRET_KEY_HERE"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    daily_report_file: str = "latest_daily_report.json"
    auto_trade_enabled: bool = True
    trade_amount: float = 1.0  # Default trade volume for auto-trading

settings = Settings()
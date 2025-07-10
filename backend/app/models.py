from pydantic import BaseModel
from typing import Optional, Any, Dict

class User(BaseModel):
    username: str
    password: str  # store hashed password!
    api_key: str
    api_key_password: str
    use_demo: bool
    cc_session_token: Optional[str] = None
    temp_cc_login_data: Optional[Any] = None
    account_info: Optional[Dict[str, Any]] = None  # <-- Add this line

    # For DB migration, add ID, created_at, updated_at as needed
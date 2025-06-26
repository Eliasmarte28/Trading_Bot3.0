from pydantic import BaseModel
from typing import Optional, Any

class User(BaseModel):
    username: str
    password: str
    api_key: str
    api_key_password: str
    use_demo: bool
    cc_session_token: Optional[str] = None
    temp_cc_login_data: Optional[Any] = None
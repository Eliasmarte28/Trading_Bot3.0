from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    api_key: str = ""
    api_key_password: str = ""
    use_demo: bool = True
    cc_session_token: str = ""      # <-- Capital.com session token
    temp_cc_login_data: dict = None # <-- Temporary 2FA context
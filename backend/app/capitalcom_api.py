import requests

class CapitalComAPI:
    def __init__(self, email=None, password=None, api_key=None, api_key_password=None, demo=True, session_token=None, login_context=None):
        self.api_base = "https://demo-api-capital.backend-capital.com" if demo else "https://api-capital.backend-capital.com"
        self.email = email
        self.password = password
        self.api_key = api_key
        self.api_key_password = api_key_password
        self.session_token = session_token
        self.login_context = login_context

    def get_login_context(self):
        # Return info needed to continue login for 2FA (could be a token or just re-use credentials)
        return {
            "email": self.email,
            "password": self.password,
            "api_key": self.api_key,
            "api_key_password": self.api_key_password,
            "demo": self.api_base.endswith("demo-api-capital.backend-capital.com")
        }

    def login(self, otp=None):
        url = f"{self.api_base}/api/v2/session"
        payload = {
            "email": self.email,
            "password": self.password,
            "apiKey": self.api_key,
            "apiKeyPassword": self.api_key_password
        }
        if otp:
            payload["oneTimePasscode"] = otp
        try:
            resp = requests.post(url, json=payload)
            data = resp.json()
            if resp.status_code == 403 and "oneTimePasscode" in data.get("message", ""):
                return {"2fa_required": True}
            if "CST" in resp.headers:
                # Login successful, session token in header
                return {
                    "success": True,
                    "session_token": resp.headers["CST"]
                }
            elif data.get("errorCode") == "error.security.one_time_passcode.required":
                return {"2fa_required": True}
            else:
                return {
                    "success": False,
                    "error": data.get("message", "Unknown error")
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_account_info(self):
        url = f"{self.api_base}/api/v2/accounts"
        headers = {"Authorization": f"Bearer {self.session_token}"}
        resp = requests.get(url, headers=headers)
        return resp.json()

    def place_order(self, symbol, side, amount, take_profit=None, stop_loss=None):
        # Implement according to Capital.com API docs
        # Use self.session_token for auth
        pass

    def get_trades(self):
        # Implement according to Capital.com API docs
        # Use self.session_token for auth
        pass
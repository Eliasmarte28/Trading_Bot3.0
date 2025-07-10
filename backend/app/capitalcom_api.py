import requests
import numpy as np
import time

class CapitalComAPI:
    def __init__(self, identifier, password, api_key, demo, login_context=None):
        self.identifier = identifier
        self.password = password
        self.api_key = api_key
        self.demo = demo
        self.login_context = login_context
        self.session_token = None  # Store the session token if available
        # Capital.com base URL
        self.base_url = (
            "https://api-capital.backend-capital.com"
            if not demo else
            "https://demo-api-capital.backend-capital.com"
        )

    def get_login_context(self):
        # Placeholder for storing intermediate login/2FA state if needed
        return {"identifier": self.identifier}

    def login(self, otp=None):
        url = f"{self.base_url}/api/v1/session"
        headers = {
            "Content-Type": "application/json",
            "X-CAP-API-KEY": self.api_key,
        }
        payload = {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False,
        }
        if otp:
            payload["2faCode"] = otp
        try:
            resp = requests.post(url, json=payload, headers=headers)
            data = resp.json()
            print("Capital.com API response:", data)  # For debugging
            # Store session token if present
            if resp.status_code == 200 and "session" in data:
                self.session_token = data["session"]
            if resp.status_code == 200 and "currentAccountId" in data:
                # Success! Return all relevant account info.
                result = {"success": True}
                result.update(data)
                return result
            elif data.get("2fa_required") or data.get("2faRequired"):
                return {"success": False, "2fa_required": True}
            else:
                return {"success": False, "error": data.get("error", "Login failed")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_account_info(self):
        url = f"{self.base_url}/api/v1/accounts"
        headers = {
            "X-CAP-API-KEY": self.api_key,
        }
        # Add Authorization header if session_token is present
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        try:
            resp = requests.get(url, headers=headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_trades(self):
        url = f"{self.base_url}/api/v1/history/transactions"
        headers = {
            "X-CAP-API-KEY": self.api_key,
        }
        # Add Authorization header if session_token is present
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        try:
            resp = requests.get(url, headers=headers)
            data = resp.json()
            return data.get("transactions", [])
        except Exception as e:
            return []

    def place_trade(self, symbol, side, amount, take_profit=None, stop_loss=None):
        url = f"{self.base_url}/api/v1/orders"
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        # Add Authorization header if session_token is present
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        payload = {
            "epic": symbol,
            "direction": side.upper(),
            "size": amount,
            "orderType": "MARKET",
        }
        if take_profit:
            payload["takeProfit"] = take_profit
        if stop_loss:
            payload["stopLoss"] = stop_loss
        try:
            resp = requests.post(url, json=payload, headers=headers)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
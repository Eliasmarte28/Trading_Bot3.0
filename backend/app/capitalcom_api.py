import requests

class CapitalComAPI:
    """
    Capital.com API client for real-world trading.
    Replace all NotImplementedError sections with real HTTP request code.
    Use self.session_token for all authenticated requests.
    """
    BASE_URL_LIVE = "https://api-capital.backend-capital.com"
    BASE_URL_DEMO = "https://demo-api-capital.backend-capital.com"

    def __init__(self, email, password, api_key, api_key_password, demo, login_context=None):
        self.email = email
        self.password = password
        self.api_key = api_key
        self.api_key_password = api_key_password
        self.demo = demo
        self.login_context = login_context
        self.session_token = None  # Set after successful login

    def login(self, otp=None):
        """
        Log in to Capital.com and obtain a session token.
        Implement actual HTTP POST to /api/v1/session as per docs:
        https://open-api.capital.com/#tag/Session
        """
        url = f"{self.BASE_URL_DEMO if self.demo else self.BASE_URL_LIVE}/api/v1/session"
        payload = {
            "email": self.email,
            "password": self.password,
            "apiKey": self.api_key,
            "apiKeyPassword": self.api_key_password
        }
        if otp:
            payload["otp"] = otp
        # TODO: Replace next line with real HTTP POST request and error handling
        raise NotImplementedError("Implement Capital.com login here and return {'success': True, 'session_token': ...} or handle 2FA.")
        # On success, set self.session_token = ... (from response)

    def get_login_context(self):
        """
        If 2FA is needed, store any context required to continue the login after OTP.
        """
        # TODO: Implement as needed for 2FA context
        return {}

    def get_account_info(self):
        """
        Get account info from Capital.com.
        Use self.session_token for authenticated requests.
        Implement GET /api/v1/accounts/me as per docs.
        """
        # url = ...
        # headers = {"Authorization": f"Bearer {self.session_token}"}
        # response = requests.get(url, headers=headers)
        # return response.json()
        raise NotImplementedError("Implement Capital.com account info retrieval here.")

    def place_trade(self, symbol, side, amount, take_profit, stop_loss):
        """
        Place a trade on Capital.com.
        Use self.session_token for authentication.
        """
        raise NotImplementedError("Implement Capital.com trade placement here.")

    def get_trades(self):
        """
        Get all trades for the account.
        Use self.session_token for authentication.
        """
        raise NotImplementedError("Implement Capital.com trades retrieval here.")
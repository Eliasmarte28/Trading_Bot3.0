import axios from "axios";

// Login without 2FA (initial attempt)
export function login(username, password, apiKey, apiKeyPassword, useDemo) {
  return axios.post("/login", {
    username,
    password,
    api_key: apiKey,
    api_key_password: apiKeyPassword,
    use_demo: useDemo,
  });
}

// Login with 2FA (OTP)
export function login2fa(username, password, apiKey, apiKeyPassword, useDemo, otp) {
  return axios.post("/login-2fa", {
    username,
    password,
    api_key: apiKey,
    api_key_password: apiKeyPassword,
    use_demo: useDemo,
    otp,
  });
}

// Get Daily Report
export function getDailyReport() {
  return axios.get("/daily-report");
}

// Get Account Info (requires token)
export function getAccount(token) {
  return axios.get("/account", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// Place Trade (requires token)
export function placeTrade(token, symbol, side, amount, take_profit, stop_loss) {
  return axios.post("/trade", {
    symbol,
    side,
    amount,
    take_profit,
    stop_loss,
  }, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// Get Trades (requires token)
export function getTrades(token) {
  return axios.get("/trades", {
    headers: { Authorization: `Bearer ${token}` }
  });
}
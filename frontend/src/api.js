import axios from "axios";

// Set the base URL for all axios requests
axios.defaults.baseURL = "http://localhost:8000";

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

// Get Daily Report (requires token)
export function getDailyReport(token) {
  return axios.get("/daily-report", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// Get Account Info (requires token)
export function getAccount(token) {
  return axios.get("/account", {
    headers: { Authorization: `Bearer ${token}` }
  });
}

// Place Trade (requires token)
// Call this with individual arguments, NOT an object:
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
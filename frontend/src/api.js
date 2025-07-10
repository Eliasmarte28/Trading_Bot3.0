const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Signup
export async function signup(data) {
  const res = await fetch(`${API_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// Login
export async function login(data) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

// Get Account Info
export async function getAccount(token) {
  const res = await fetch(`${API_URL}/account`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

// Place Trade
export async function placeTrade(token, symbol, side, amount, take_profit, stop_loss) {
  const res = await fetch(`${API_URL}/trade`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ symbol, side, amount, take_profit, stop_loss }),
  });
  return res.json();
}

// Get Trades
export async function getTrades(token) {
  const res = await fetch(`${API_URL}/trades`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

// Get Daily Report
export async function getDailyReport(token) {
  const res = await fetch(`${API_URL}/daily-report`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.json();
}

// Get Risk Settings
export async function getRiskSettings(token) {
  const res = await fetch(`${API_URL}/risk-settings`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch risk settings");
  return res.json();
}

// Set Risk Settings
export async function setRiskSettings(token, settings) {
  const res = await fetch(`${API_URL}/risk-settings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error("Failed to save risk settings");
  return res.json();
}
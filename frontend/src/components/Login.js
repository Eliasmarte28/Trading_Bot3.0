import React, { useState } from "react";
import { login, login2fa } from "../api";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [apiKeyPassword, setApiKeyPassword] = useState("");
  const [useDemo, setUseDemo] = useState(true);
  const [otp, setOtp] = useState("");
  const [showOtp, setShowOtp] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await login(
        username,
        password,
        apiKey,
        apiKeyPassword,
        useDemo
      );
      if (res.data && res.data["2fa_required"]) {
        setShowOtp(true);
      } else if (res.data && res.data.access_token) {
        onLogin(res.data.access_token);
      } else {
        setError("Login failed. Please check your credentials.");
      }
    } catch (err) {
      setError("Login failed. Check credentials and API key.");
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await login2fa(
        username,
        password,
        apiKey,
        apiKeyPassword,
        useDemo,
        otp
      );
      if (res.data && res.data.access_token) {
        onLogin(res.data.access_token);
      } else {
        setError("2FA failed. Please try again.");
      }
    } catch (err) {
      setError("2FA failed. Please try again.");
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "auto", marginTop: 100 }}>
      <h2>Capital.com Bot Login</h2>
      {!showOtp ? (
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
          <input
            type="text"
            placeholder="Capital.com API Key"
            required
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
          <input
            type="password"
            placeholder="API Key Password"
            required
            value={apiKeyPassword}
            onChange={(e) => setApiKeyPassword(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
          <label>
            <input
              type="checkbox"
              checked={useDemo}
              onChange={(e) => setUseDemo(e.target.checked)}
            />{" "}
            Use Demo Account
          </label>
          <button type="submit" style={{ width: "100%", marginTop: 15 }}>
            Login
          </button>
          {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
        </form>
      ) : (
        <form onSubmit={handleOtpSubmit}>
          <input
            type="text"
            placeholder="Enter 2FA code"
            required
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
          <button type="submit" style={{ width: "100%", marginTop: 15 }}>
            Submit 2FA code
          </button>
          {error && <div style={{ color: "red", marginTop: 10 }}>{error}</div>}
        </form>
      )}
    </div>
  );
}

export default Login;
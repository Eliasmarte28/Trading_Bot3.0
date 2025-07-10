import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { signup, login, getTrades, getDailyReport } from "./api";
import Dashboard from "./Dashboard";

function LoginSignup({ onLogin }) {
  const [signupData, setSignupData] = useState({
    username: "",
    password: "",
    api_key: "",
    api_key_password: "",
    use_demo: true,
  });
  const [loginData, setLoginData] = useState({
    username: "",
    password: "",
    api_key: "",
    api_key_password: "",
    use_demo: true,
  });
  const [signupResult, setSignupResult] = useState(null);
  const [loginResult, setLoginResult] = useState(null);

  const handleSignup = async (e) => {
    e.preventDefault();
    const result = await signup(signupData);
    setSignupResult(result);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const result = await login(loginData);
    setLoginResult(result);
    if (result && result.access_token) {
      onLogin(result.access_token, loginData.username);
    }
  };

  return (
    <div>
      <h2>Signup</h2>
      <form onSubmit={handleSignup}>
        <input placeholder="Email" value={signupData.username} onChange={e => setSignupData({ ...signupData, username: e.target.value })} />
        <input placeholder="Password" type="password" value={signupData.password} onChange={e => setSignupData({ ...signupData, password: e.target.value })} />
        <input placeholder="API Key" value={signupData.api_key} onChange={e => setSignupData({ ...signupData, api_key: e.target.value })} />
        <input placeholder="API Key Password" value={signupData.api_key_password} onChange={e => setSignupData({ ...signupData, api_key_password: e.target.value })} />
        <label>
          Use Demo:
          <input type="checkbox" checked={signupData.use_demo} onChange={e => setSignupData({ ...signupData, use_demo: e.target.checked })} />
        </label>
        <button type="submit">Sign Up</button>
      </form>
      <pre>{signupResult && JSON.stringify(signupResult, null, 2)}</pre>

      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input placeholder="Email" value={loginData.username} onChange={e => setLoginData({ ...loginData, username: e.target.value })} />
        <input placeholder="Password" type="password" value={loginData.password} onChange={e => setLoginData({ ...loginData, password: e.target.value })} />
        <input placeholder="API Key" value={loginData.api_key} onChange={e => setLoginData({ ...loginData, api_key: e.target.value })} />
        <input placeholder="API Key Password" value={loginData.api_key_password} onChange={e => setLoginData({ ...loginData, api_key_password: e.target.value })} />
        <label>
          Use Demo:
          <input type="checkbox" checked={loginData.use_demo} onChange={e => setLoginData({ ...loginData, use_demo: e.target.checked })} />
        </label>
        <button type="submit">Login</button>
      </form>
      <pre>{loginResult && JSON.stringify(loginResult, null, 2)}</pre>
    </div>
  );
}

function Trades({ token, onBack }) {
  const [trades, setTrades] = useState(null);
  React.useEffect(() => {
    getTrades(token).then(setTrades);
  }, [token]);
  return (
    <div>
      <button onClick={onBack}>Back to Dashboard</button>
      <h2>Trades</h2>
      {trades ? <pre>{JSON.stringify(trades, null, 2)}</pre> : <p>Loading...</p>}
    </div>
  );
}

function DailyReport({ token, onBack }) {
  const [report, setReport] = useState(null);
  React.useEffect(() => {
    getDailyReport(token).then(setReport);
  }, [token]);
  return (
    <div>
      <button onClick={onBack}>Back to Dashboard</button>
      <h2>Daily Asset Report</h2>
      {report ? <pre>{JSON.stringify(report, null, 2)}</pre> : <p>Loading...</p>}
    </div>
  );
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("accessToken"));
  const [username, setUsername] = useState(() => localStorage.getItem("username"));

  const handleLogin = (tok, user) => {
    setToken(tok);
    setUsername(user);
    localStorage.setItem("accessToken", tok);
    localStorage.setItem("username", user);
  };
  const handleLogout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
  };

  return (
    <Router>
      <Routes>
        {!token ? (
          <Route path="*" element={<LoginSignup onLogin={handleLogin} />} />
        ) : (
          <>
            <Route path="/" element={<Dashboard token={token} onLogout={handleLogout} username={username} />} />
            <Route path="/dashboard" element={<Dashboard token={token} onLogout={handleLogout} username={username} />} />
            <Route path="/trades" element={<Trades token={token} onBack={() => window.history.back()} />} />
            <Route path="/daily-report" element={<DailyReport token={token} onBack={() => window.history.back()} />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </>
        )}
      </Routes>
    </Router>
  );
}

export default App;
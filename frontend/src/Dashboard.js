import React, { useEffect, useState } from "react";
import { getAccount, placeTrade, getRiskSettings } from "./api";
import { useNavigate } from "react-router-dom";
import RiskSettings from "./RiskSettings";

function RiskSettingsSummary({ token }) {
  const [risk, setRisk] = useState(null);

  useEffect(() => {
    async function fetchRisk() {
      try {
        let data = null;
        if (token) {
          data = await getRiskSettings(token);
        }
        if (!data || typeof data.concurrentTrades === "undefined") {
          const local = localStorage.getItem("riskSettings");
          data = local ? JSON.parse(local) : null;
        }
        setRisk(data);
      } catch (e) {
        setRisk(null);
      }
    }
    fetchRisk();
  }, [token]);

  if (!risk) return null;
  return (
    <div style={{border:"1px solid #d4e6fa", borderRadius:8, background:"#f6fafd", padding:12, marginBottom:18, fontSize:15}}>
      <b>Current Risk Settings:</b><br />
      Concurrent Trades: <b>{risk.concurrentTrades}</b>, 
      Risk/Trade: <b>{risk.riskPerTrade}%</b>, 
      Max Daily Loss: <b>${risk.maxDailyLoss}</b>,<br/>
      Profit Target: <b>${risk.profitTarget}</b>, 
      Leverage: <b>{risk.leverage}x</b>
    </div>
  );
}

function Dashboard({ token, username, onLogout }) {
  const [account, setAccount] = useState(null);
  const [symbol, setSymbol] = useState("EURUSD");
  const [side, setSide] = useState("BUY");
  const [amount, setAmount] = useState(1);
  const [takeProfit, setTakeProfit] = useState("");
  const [stopLoss, setStopLoss] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tradeLoading, setTradeLoading] = useState(false);
  const [showRiskSettings, setShowRiskSettings] = useState(false);
  const navigate = useNavigate();

  // Fetch account info with error and loading state
  const fetchAccount = () => {
    setLoading(true);
    setError("");
    getAccount(token)
      .then((data) => {
        setAccount(data);
        setError("");
      })
      .catch(() => {
        setError("Failed to fetch account info.");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAccount();
    // eslint-disable-next-line
  }, [token]);

  // Trade form validation and submission
  const handleTrade = async (e) => {
    e.preventDefault();
    setMessage("");
    if (!symbol.trim() || isNaN(amount) || Number(amount) <= 0) {
      setMessage("Please provide a valid symbol and amount.");
      return;
    }
    setTradeLoading(true);
    try {
      const res = await placeTrade(
        token,
        symbol,
        side,
        Number(amount),
        takeProfit ? Number(takeProfit) : undefined,
        stopLoss ? Number(stopLoss) : undefined
      );
      if (res && res.success) {
        setMessage("✅ Trade placed!");
        fetchAccount(); // Refresh balance after trade
      } else {
        setMessage("❌ Trade error: " + (res.detail || JSON.stringify(res)));
      }
    } catch (err) {
      setMessage("❌ Error placing trade.");
    }
    setTradeLoading(false);
  };

  // Helper to render account info
  const renderAccountInfo = () => {
    if (loading) return <p>Loading...</p>;
    if (error) return <p style={{ color: "red" }}>{error}</p>;
    if (!account) return <p>No account info found.</p>;

    const { accountType, accountInfo = {}, currencyIsoCode, currencySymbol, clientId, currentAccountId } = account;

    return (
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 8,
          padding: 16,
          marginBottom: 24,
          maxWidth: 380,
          background: "#fafbfc"
        }}
        aria-label="Account Information"
      >
        <table style={{ width: "100%" }}>
          <tbody>
            <tr>
              <th align="left">Account Type:</th>
              <td>{accountType}</td>
            </tr>
            <tr>
              <th align="left">Balance:</th>
              <td>
                {accountInfo.balance} {currencyIsoCode} ({currencySymbol})
              </td>
            </tr>
            <tr>
              <th align="left">Profit/Loss:</th>
              <td>
                {accountInfo.profitLoss} {currencyIsoCode}
              </td>
            </tr>
            <tr>
              <th align="left">Deposit:</th>
              <td>
                {accountInfo.deposit} {currencyIsoCode}
              </td>
            </tr>
            <tr>
              <th align="left">Available:</th>
              <td>
                {accountInfo.available} {currencyIsoCode}
              </td>
            </tr>
            <tr>
              <th align="left">Client ID:</th>
              <td>{clientId}</td>
            </tr>
            <tr>
              <th align="left">Account ID:</th>
              <td>{currentAccountId}</td>
            </tr>
          </tbody>
        </table>
        <button onClick={fetchAccount} style={{ marginTop: 12 }}>⟳ Refresh</button>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: 600, margin: "36px auto", fontFamily: "Segoe UI, sans-serif" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 style={{ margin: 0 }}>Dashboard</h2>
        <button onClick={onLogout} aria-label="Logout" style={{ background: "#eee", border: "1px solid #ccc", borderRadius: 4, padding: "4px 16px" }}>Logout</button>
      </div>
      <h3>Welcome, {username}!</h3>
      <RiskSettingsSummary token={token} />
      <button
        onClick={() => setShowRiskSettings(true)}
        style={{
          padding: "8px 14px",
          borderRadius: 4,
          border: "1px solid #0066ea",
          background: "#e7f1ff",
          color: "#0066ea",
          marginBottom: 18,
          fontWeight: 500
        }}>
        Risk & Trade Settings
      </button>
      {showRiskSettings && (
        <RiskSettings token={token} onClose={() => setShowRiskSettings(false)} />
      )}
      <h3>Account Info</h3>
      {renderAccountInfo()}

      <h3>Place Trade</h3>
      <form onSubmit={handleTrade} style={{ marginBottom: 20, display: "flex", flexWrap: "wrap", alignItems: "center", gap: 8 }}>
        <input
          type="text"
          value={symbol}
          onChange={e => setSymbol(e.target.value)}
          placeholder="Symbol (e.g. EURUSD)"
          required
          style={{ width: 100 }}
        />
        <select value={side} onChange={e => setSide(e.target.value)}>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <input
          type="number"
          value={amount}
          min="0.01"
          step="0.01"
          onChange={e => setAmount(e.target.value)}
          placeholder="Amount"
          required
          style={{ width: 80 }}
        />
        <input
          type="number"
          value={takeProfit}
          onChange={e => setTakeProfit(e.target.value)}
          placeholder="Take Profit (optional)"
          style={{ width: 120 }}
          aria-label="Take Profit"
        />
        <input
          type="number"
          value={stopLoss}
          onChange={e => setStopLoss(e.target.value)}
          placeholder="Stop Loss (optional)"
          style={{ width: 120 }}
          aria-label="Stop Loss"
        />
        <button
          type="submit"
          disabled={tradeLoading || loading}
          style={{ background: "#0066ea", color: "white", border: "none", borderRadius: 4, padding: "6px 16px", fontWeight: 500, cursor: tradeLoading || loading ? "not-allowed" : "pointer" }}
        >
          {tradeLoading ? "Placing..." : "Trade"}
        </button>
      </form>
      {message && <div style={{ margin: "12px 0", color: message.startsWith("✅") ? "green" : "red", fontWeight: 500 }}>{message}</div>}

      <div style={{ display: "flex", gap: 12 }}>
        <button onClick={() => navigate("/trades")} style={{ padding: "8px 14px", borderRadius: 4, border: "1px solid #ccc", background: "#f4f6fa" }}>
          Review Trades
        </button>
        <button onClick={() => navigate("/daily-report")} style={{ padding: "8px 14px", borderRadius: 4, border: "1px solid #ccc", background: "#f4f6fa" }}>
          View Daily Report
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
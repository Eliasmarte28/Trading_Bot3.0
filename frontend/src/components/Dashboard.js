import React, { useEffect, useState } from "react";
import { getAccount, placeTrade } from "../api";
import { useNavigate } from "react-router-dom";

function Dashboard({ token, onLogout }) {
  const [account, setAccount] = useState(null);
  const [symbol, setSymbol] = useState("EURUSD");
  const [side, setSide] = useState("BUY");
  const [amount, setAmount] = useState(1);
  const [message, setMessage] = useState("");
  const [takeProfit, setTakeProfit] = useState("");
  const [stopLoss, setStopLoss] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getAccount(token).then((res) => setAccount(res.data));
  }, [token]);

  const handleTrade = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await placeTrade(
        token,
        symbol,
        side,
        Number(amount),
        takeProfit ? Number(takeProfit) : undefined,
        stopLoss ? Number(stopLoss) : undefined
      );
      setMessage("Trade placed!");
    } catch {
      setMessage("Error placing trade.");
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", marginTop: 40 }}>
      <h2>Dashboard</h2>
      <button onClick={onLogout} style={{ float: "right" }}>
        Logout
      </button>
      <h3>Account Info</h3>
      {account ? (
        <pre>{JSON.stringify(account, null, 2)}</pre>
      ) : (
        <p>Loading...</p>
      )}
      <h3>Place Trade</h3>
      <form onSubmit={handleTrade}>
        <input
          type="text"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
          placeholder="Symbol (e.g. EURUSD)"
          style={{ marginRight: 10 }}
        />
        <select value={side} onChange={(e) => setSide(e.target.value)}>
          <option value="BUY">BUY</option>
          <option value="SELL">SELL</option>
        </select>
        <input
          type="number"
          value={amount}
          min="0.01"
          step="0.01"
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Amount"
          style={{ marginLeft: 10, marginRight: 10 }}
        />
        <input
          type="number"
          value={takeProfit}
          onChange={(e) => setTakeProfit(e.target.value)}
          placeholder="Take Profit (optional)"
          style={{ marginLeft: 10, marginRight: 10 }}
        />
        <input
          type="number"
          value={stopLoss}
          onChange={(e) => setStopLoss(e.target.value)}
          placeholder="Stop Loss (optional)"
          style={{ marginLeft: 10, marginRight: 10 }}
        />
        <button type="submit">Trade</button>
      </form>
      {message && <p>{message}</p>}
      <button onClick={() => navigate("/trades")} style={{ marginTop: 20 }}>
        Review Trades
      </button>
      <button onClick={() => navigate("/daily-report")} style={{ marginTop: 10, marginLeft: 10 }}>
        View Daily Report
      </button>
    </div>
  );
}

export default Dashboard;
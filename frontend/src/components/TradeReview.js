import React, { useEffect, useState } from "react";
import { getTrades } from "../api";
import { useNavigate } from "react-router-dom";

function TradeReview({ token, onLogout }) {
  const [trades, setTrades] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    getTrades(token).then((res) => setTrades(res.data));
  }, [token]);

  return (
    <div style={{ maxWidth: 600, margin: "auto", marginTop: 40 }}>
      <h2>Trade Review</h2>
      <button onClick={onLogout} style={{ float: "right" }}>
        Logout
      </button>
      <button onClick={() => navigate("/")}>Back to Dashboard</button>
      <table style={{ width: "100%", marginTop: 20, borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Trade ID</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Profit</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(trades) &&
            trades.map((trade, i) => (
              <tr key={i}>
                <td>{trade.trade_id || trade.id || "?"}</td>
                <td>{trade.symbol || trade.market || "?"}</td>
                <td>{trade.side}</td>
                <td>{trade.amount || trade.quantity || "?"}</td>
                <td>{trade.status || trade.state || "?"}</td>
                <td>{trade.profit || trade.realized || "?"}</td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}

export default TradeReview;
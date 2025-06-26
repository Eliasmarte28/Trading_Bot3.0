import React, { useEffect, useState } from "react";
import { getDailyReport } from "../api";
import { useNavigate } from "react-router-dom";

function DailyReport({ onLogout }) {
  const [report, setReport] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      navigate("/login");
      return;
    }
    getDailyReport(token)
      .then((res) => setReport(res.data))
      .catch((err) => {
        if (err.response && err.response.status === 401) {
          onLogout();
        }
      });
  }, [navigate, onLogout]);

  return (
    <div style={{ maxWidth: 800, margin: "auto", marginTop: 40 }}>
      <h2>Daily Asset Report</h2>
      <button onClick={onLogout} style={{ float: "right" }}>
        Logout
      </button>
      <button onClick={() => navigate("/")}>Back to Dashboard</button>
      {report ? (
        <div>
          <p>Report Date: {report.date}</p>
          <h4>Auto-Trades Executed</h4>
          <table style={{ width: "100%", marginTop: 10, borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Side</th>
                <th>Response</th>
              </tr>
            </thead>
            <tbody>
              {report.auto_trades && report.auto_trades.map((trade, i) => (
                <tr key={i}>
                  <td>{trade.symbol}</td>
                  <td>{trade.side}</td>
                  <td>
                    <pre style={{fontSize:'0.9em',whiteSpace:'pre-wrap'}}>{JSON.stringify(trade.response, null, 2)}</pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <h4>Top Assets to Watch</h4>
          <table style={{ width: "100%", marginTop: 20, borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Signals/Why</th>
              </tr>
            </thead>
            <tbody>
              {report.assets.map((a, i) => (
                <tr key={i}>
                  <td>{a.symbol}</td>
                  <td>{a.signals.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>Loading daily report...</p>
      )}
    </div>
  );
}

export default DailyReport;
import React, { useState, useEffect } from "react";
import { getRiskSettings, setRiskSettings } from "./api";

const DEFAULT_SETTINGS = {
  concurrentTrades: 1,
  riskPerTrade: 2,
  maxDailyLoss: 20,
  profitTarget: 50,
  leverage: 10,
};

export default function RiskSettings({ token, onClose }) {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        let data;
        if (token) {
          data = await getRiskSettings(token);
        }
        if (!data || typeof data.concurrentTrades === "undefined") {
          const local = localStorage.getItem("riskSettings");
          data = local ? JSON.parse(local) : DEFAULT_SETTINGS;
        }
        setSettings(data);
      } catch (e) {
        setError("Failed to load settings.");
      }
    }
    load();
  }, [token]);

  const handleChange = (key, value) => {
    setSettings((s) => ({ ...s, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError("");
    try {
      if (token) await setRiskSettings(token, settings);
      localStorage.setItem("riskSettings", JSON.stringify(settings));
      setSaving(false);
      if (onClose) onClose();
    } catch (e) {
      setSaving(false);
      setError("Failed to save settings.");
    }
  };

  return (
    <div style={{padding:24, maxWidth:400, margin:"32px auto", background:"#fafafa", borderRadius:8, boxShadow:"0 2px 12px #0001", position:"relative"}}>
      <h2 style={{marginTop:0}}>Risk & Trade Management</h2>
      <label style={{display:"block", marginBottom:10}}>
        Number of Concurrent Trades
        <input
          type="number"
          min={1}
          max={showAdvanced ? 10 : 1}
          value={settings.concurrentTrades}
          onChange={e => handleChange("concurrentTrades", Number(e.target.value))}
          disabled={!showAdvanced}
          style={{marginLeft:8, width: 50}}
        />
        <span style={{fontSize:12, color:"#888", marginLeft:6}}>Default: 1 (Qtrading style)</span>
      </label>
      <label style={{display:"block", marginBottom:10}}>
        Risk Per Trade (% of Balance)
        <input
          type="number"
          min={0.5}
          max={showAdvanced ? 10 : 2}
          step={0.1}
          value={settings.riskPerTrade}
          onChange={e => handleChange("riskPerTrade", Number(e.target.value))}
          style={{marginLeft:8, width: 50}}
        />
        <span style={{fontSize:12, color:"#888", marginLeft:6}}>Recommended: 1–2%</span>
      </label>
      <label style={{display:"block", marginBottom:10}}>
        Max Daily Loss ($)
        <input
          type="number"
          min={1}
          max={999999}
          value={settings.maxDailyLoss}
          onChange={e => handleChange("maxDailyLoss", Number(e.target.value))}
          style={{marginLeft:8, width: 60}}
        />
      </label>
      <label style={{display:"block", marginBottom:10}}>
        Profit Target ($)
        <input
          type="number"
          min={1}
          max={999999}
          value={settings.profitTarget}
          onChange={e => handleChange("profitTarget", Number(e.target.value))}
          style={{marginLeft:8, width: 60}}
        />
      </label>
      <label style={{display:"block", marginBottom:10}}>
        Leverage
        <input
          type="number"
          min={1}
          max={100}
          value={settings.leverage}
          onChange={e => handleChange("leverage", Number(e.target.value))}
          style={{marginLeft:8, width: 50}}
        />
        <span style={{fontSize:12, color:"#888", marginLeft:6}}>Use with caution!</span>
      </label>
      <button onClick={() => setShowAdvanced(v => !v)} style={{marginTop:10, marginRight: 8}}>
        {showAdvanced ? "Hide Advanced" : "Show Advanced"}
      </button>
      <button onClick={handleSave} disabled={saving} style={{marginTop:10, marginRight: 8}}>
        {saving ? "Saving..." : "Save"}
      </button>
      <button onClick={onClose} style={{marginTop:10}}>Cancel</button>
      {error && <div style={{color:"red", marginTop:10}}>{error}</div>}
      {showAdvanced && (
        <div style={{marginTop:12, fontSize:12, color:"#e67e22"}}>
          Advanced: Higher risk settings can lead to faster gains and losses.
        </div>
      )}
    </div>
  );
}
// pages/Security.jsx — with real UEBA data + PDF download
import { useState, useEffect } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://192.168.249.221:8000";
const cfg = { headers: { "ngrok-skip-browser-warning": "true" } };

export default function Security() {
  const [status,     setStatus]     = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      const [statusRes, activityRes] = await Promise.all([
        axios.get(`${API}/ueba/status`,   cfg),
        axios.get(`${API}/ueba/activity`, cfg),
      ]);
      setStatus(statusRes.data);
      setActivities(activityRes.data.activities || []);
    } catch (e) {
      console.error("UEBA load failed:", e.message);
    } finally {
      setLoading(false);
    }
  }

  async function downloadUEBAPdf() {
    setDownloading(true);
    try {
      const response = await fetch(`${API}/ueba/pdf`, {
        headers: { "ngrok-skip-browser-warning": "true" }
      });
      if (!response.ok) throw new Error("PDF generation failed");
      const blob = await response.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `UEBA_Security_Report_${new Date().toISOString().slice(0,10)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("PDF download failed: " + e.message);
    } finally {
      setDownloading(false);
    }
  }

  const scoreColor = (score) =>
    score >= 70 ? "#ff4560" : score >= 40 ? "#ffaa00" : "#00e396";

  const riskBg = (score) =>
    score >= 70 ? "bg-red-500/10 border-red-500/30"
    : score >= 40 ? "bg-yellow-500/10 border-yellow-500/30"
    : "bg-gray-800 border-white/5";

  return (
    <div className="pt-14 min-h-screen p-5" style={{ background: "transparent" }}>
      <div className="mb-6 flex justify-between items-end">
        <div>
          <p className="text-xs text-white/30 tracking-widest uppercase mb-1">UEBA Monitor</p>
          <h1 className="text-2xl font-bold text-white">Security Intelligence</h1>
        </div>
        {/* ── PDF Download Button ── */}
        <button
          onClick={downloadUEBAPdf}
          disabled={downloading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all"
          style={{
            background: downloading ? "rgba(255,255,255,0.05)" : "rgba(168,85,247,0.15)",
            border:     `1px solid ${downloading ? "rgba(255,255,255,0.1)" : "rgba(168,85,247,0.4)"}`,
            color:      downloading ? "rgba(255,255,255,0.3)" : "#a855f7",
          }}
        >
          {downloading ? "⏳ Generating..." : "📄 Download UEBA Report PDF"}
        </button>
      </div>

      {/* Status Banner */}
      {status && (
        <div className={`rounded-xl p-5 mb-6 border flex items-center justify-between ${
          status.flagged > 0
            ? "bg-red-900/20 border-red-500/40"
            : "bg-green-900/20 border-green-500/30"
        }`}>
          <div className="flex items-center gap-4">
            <div className="text-4xl">{status.flagged > 0 ? "🚨" : "🛡️"}</div>
            <div>
              <div className={`text-xl font-bold ${status.flagged > 0 ? "text-red-400" : "text-green-400"}`}>
                {status.flagged > 0 ? "Anomaly Detected" : "System Secure"}
              </div>
              <div className="text-white/50 text-sm mt-1">{status.message}</div>
            </div>
          </div>
          <div className="grid grid-cols-4 gap-6 text-center">
            {[
              { label: "Monitored", value: status.monitored, color: "text-cyan-400"   },
              { label: "Flagged",   value: status.flagged,   color: "text-red-400"    },
              { label: "Blocked",   value: status.blocked,   color: "text-orange-400" },
              { label: "Normal",    value: status.normal,    color: "text-green-400"  },
            ].map(s => (
              <div key={s.label}>
                <div className={`text-2xl font-black ${s.color}`}>{s.value}</div>
                <div className="text-xs text-white/40">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Log */}
      <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold text-white">Activity Log — Today</h2>
          <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-1 rounded-full">
            {activities.length} events
          </span>
        </div>

        {loading && (
          <div className="text-center py-8 text-white/30">Loading UEBA data...</div>
        )}

        {!loading && activities.length === 0 && (
          <div className="text-center py-8 text-white/30">
            <div className="text-3xl mb-2">🔍</div>
            No activity yet — run AI analysis on a vehicle to generate UEBA events
          </div>
        )}

        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {activities.map((a, i) => (
            <div key={i} className={`flex items-start gap-4 p-3 rounded-xl border ${riskBg(a.score)}`}>
              <div className="text-xs text-white/30 w-12 shrink-0 mt-0.5">{a.time_str}</div>
              <div className="flex-1">
                <div className="text-xs text-white/50 uppercase tracking-wide">{a.agent}</div>
                <div className="text-sm font-medium text-white mt-0.5">{a.action}</div>
                {a.vehicle_id && (
                  <div className="text-xs text-white/30 mt-0.5">
                    Vehicle: {a.vehicle_id} · {a.risk_level} · {new Date(a.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
              <span className="text-xs font-black px-2 py-1 rounded-full shrink-0"
                style={{ background: scoreColor(a.score) + "20", color: scoreColor(a.score) }}>
                Score {a.score}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
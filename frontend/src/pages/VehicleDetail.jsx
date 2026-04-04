// pages/VehicleDetail.jsx — COMPLETE FINAL with PDF Download
// ─────────────────────────────────────────────────────────────

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getVehicle, analyzeVehicle, bookAppointment, submitFeedback } from "../services/api";
import { statusColor } from "../utils/helpers";

const AGENT_CONFIG = [
  { key: "DataAnalysisAgent",         icon: "📊", name: "Data Analysis"    },
  { key: "DiagnosisAgent",            icon: "🔬", name: "Diagnosis"        },
  { key: "Person2DataAnalysisAgent",  icon: "🧠", name: "Advanced Analysis"},
  { key: "Person2DiagnosisAgent",     icon: "💊", name: "P2 Diagnosis"     },
  { key: "EngagementAgent",           icon: "📞", name: "Engagement"       },
  { key: "SchedulingAgent",           icon: "📅", name: "Scheduling"       },
  { key: "FeedbackAgent",             icon: "⭐", name: "Feedback"         },
  { key: "ManufacturingInsightsAgent",icon: "🏭", name: "Manufacturing"    },
];

function getAgentSummary(agentKey, finding, vehicle) {
  if (!finding) return "No data";
  switch (agentKey) {
    case "DataAnalysisAgent":
      return `${finding.anomalies_detected?.critical_count || 0} critical · ${finding.anomalies_detected?.warning_count || 0} warning · Status: ${finding.overall_status?.toUpperCase() || "UNKNOWN"}`;
    case "DiagnosisAgent":
      return finding.ml_prediction
        ? `${finding.ml_prediction.prediction} · ${finding.ml_prediction.failure_probability}% failure risk · ${finding.ml_prediction.risk_level}`
        : finding.diagnosis || "Complete";
    case "Person2DataAnalysisAgent":
      return `Health score: ${finding.health_score ?? "—"}/100 · ${finding.critical_count || 0} critical sensors · Anomaly: ${finding.anomaly_detected ? "YES ⚠️" : "NO ✅"}`;
    case "Person2DiagnosisAgent":
      return finding.customer_message || finding.recommended_action || "Diagnosis complete";
    case "EngagementAgent": {
      const call  = finding.call_action === "call_now" ? `📞 Called ${vehicle?.owner_name}` : `⏰ Call at 9 AM`;
      const sms   = finding.sms_sent   ? "✅ SMS" : "❌ SMS";
      const email = finding.email_sent ? "✅ Email" : "❌ Email";
      return `${call} (${finding.call_outcome || "pending"}) · ${sms} · ${email}`;
    }
    case "SchedulingAgent": {
      const a = finding.appointment;
      if (!a) return finding.message || "No booking needed";
      return `✅ ${a.date} at ${a.time_slot || a.time} · ${a.service_center || "AutoNexus"}`;
    }
    case "FeedbackAgent":
      return finding.survey_required ? "Survey queued post-service" : "No survey at this stage";
    case "ManufacturingInsightsAgent": {
      const rca = finding.rca?.primary_cause || "";
      const fix = finding.capa?.corrective_actions?.[0] || "";
      return [rca && `RCA: ${rca}`, fix && `Fix: ${fix}`].filter(Boolean).join(" · ") || "Analysis complete";
    }
    default: return "Complete";
  }
}

function AgentResultCard({ agentKey, config, finding, vehicle }) {
  const color =
    agentKey === "EngagementAgent" && finding?.urgency === "CRITICAL" ? "#ff4560" :
    agentKey === "SchedulingAgent" && finding?.booking_success        ? "#00e396" :
    agentKey === "ManufacturingInsightsAgent"                         ? "#a855f7" : "#00e396";

  return (
    <div className="rounded-xl p-3 border-l-2"
      style={{ background: "rgba(255,255,255,0.03)", borderLeftColor: color, animation: "slideIn 0.4s ease" }}>
      <div className="flex items-center gap-2 mb-1.5">
        <span>{config.icon}</span>
        <span className="text-xs font-bold text-white/70 tracking-wider uppercase">{config.name}</span>
        <span className="ml-auto text-xs px-2 py-0.5 rounded-full font-bold"
          style={{ background: color + "20", color }}>● DONE</span>
      </div>
      <div className="text-xs text-white/60 leading-relaxed">
        {getAgentSummary(agentKey, finding, vehicle)}
      </div>

      {/* Issues tags */}
      {agentKey === "EngagementAgent" && finding?.issues_detected?.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {finding.issues_detected.map((issue, i) => (
            <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-red-300">{issue}</span>
          ))}
        </div>
      )}

      {/* Shop details */}
      {agentKey === "SchedulingAgent" && finding?.appointment && (
        <div className="mt-2 p-2 bg-green-500/10 rounded-lg text-xs space-y-0.5">
          <div className="text-green-300 font-semibold">
            📅 {finding.appointment.date} · {finding.appointment.time_slot || finding.appointment.time}
          </div>
          {finding.shop_details?.name && (
            <>
              <div className="text-green-300/80">🏪 {finding.shop_details.name}</div>
              <div className="text-white/40">📍 {finding.shop_details.address}</div>
              <div className="text-white/40">📞 {finding.shop_details.phone}</div>
              <div className="text-yellow-400/60">⭐ {finding.shop_details.rating}/5 · {finding.shop_details.hours}</div>
            </>
          )}
        </div>
      )}

      {/* RCA + CAPA */}
      {agentKey === "ManufacturingInsightsAgent" && finding?.capa && (
        <div className="mt-2 space-y-1">
          {finding.capa.corrective_actions?.slice(0, 2).map((a, i) => (
            <div key={i} className="text-xs text-purple-300">→ {a}</div>
          ))}
          {finding.capa.preventive_actions?.slice(0, 1).map((a, i) => (
            <div key={i} className="text-xs text-blue-300/70">🛡 {a}</div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
export default function VehicleDetail() {
  const { id }   = useParams();
  const navigate = useNavigate();

  const [vehicle,        setVehicle]       = useState(null);
  const [analysis,       setAnalysis]      = useState(null);
  const [analyzing,      setAnalyzing]     = useState(false);
  const [visibleAgents,  setVisibleAgents] = useState([]);
  const [currentAgent,   setCurrentAgent]  = useState(null);
  const [done,           setDone]          = useState(false);
  const [loading,        setLoading]       = useState(true);
  const [bookingResult,  setBookingResult] = useState(null);
  const [showBooking,    setShowBooking]   = useState(false);
  const [feedbackDone,   setFeedbackDone]  = useState(false);
  const [feedbackStar,   setFeedbackStar]  = useState(0);

  // ── NEW: PDF download states ──────────────────────────────
  const [downloadingPdf,      setDownloadingPdf]      = useState(false);
  const [downloadingFleetPdf, setDownloadingFleetPdf] = useState(false);

  // ─────────────────────────────────────────────────────────
  useEffect(() => {
    setLoading(true);
    setAnalysis(null); setVisibleAgents([]); setDone(false);
    getVehicle(id)
      .then(v => setVehicle({
        ...v,
        name:  v.model,
        owner: v.owner_name,
        sensors: {
          brakeTemp:   v.brake_temp,
          oilPressure: v.oil_pressure,
          engineTemp:  v.engine_temp,
          tirePressure:v.tire_pressure,
          brakeFluid:  v.brake_fluid_level,
        },
      }))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  // ── Run 8-agent analysis ──────────────────────────────────
  async function runAnalysis() {
    if (!vehicle) return;
    setAnalyzing(true); setVisibleAgents([]); setDone(false); setAnalysis(null);
    try {
      let step = 0;
      const interval = setInterval(() => {
        if (step < AGENT_CONFIG.length) setCurrentAgent(AGENT_CONFIG[step++].key);
      }, 500);

      const result = await analyzeVehicle(id);
      clearInterval(interval);
      setAnalysis(result);

      // Fire ChatViewer event
      window.dispatchEvent(new CustomEvent("autonexus_analysis", {
        detail: { analysis: result, vehicle }
      }));

      // Stagger reveal
      AGENT_CONFIG.forEach((a, i) => {
        setTimeout(() => {
          setCurrentAgent(a.key);
          setVisibleAgents(prev => [...prev, a.key]);
          if (i === AGENT_CONFIG.length - 1) {
            setTimeout(() => { setCurrentAgent(null); setDone(true); setAnalyzing(false); }, 400);
          }
        }, i * 200);
      });

    } catch (e) {
      setAnalyzing(false);
      alert("Analysis failed: " + e.message);
    }
  }

  // ── Book appointment ──────────────────────────────────────
  async function handleBook() {
    try {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const result = await bookAppointment({
        vehicle_id:   id,
        service_date: tomorrow.toISOString().split("T")[0],
        service_time: "09:00",
        service_type: "emergency_repair",
      });
      setBookingResult(result);
      setShowBooking(false);
    } catch (e) { alert("Booking failed: " + e.message); }
  }

  // ── Submit feedback ───────────────────────────────────────
  async function handleFeedback(star) {
    setFeedbackStar(star);
    try {
      if (bookingResult?.booking_id) {
        await submitFeedback(bookingResult.booking_id, {
          booking_id:            bookingResult.booking_id,
          vehicle_id:            id,
          overall_rating:        star,
          service_quality:       star,
          technician_knowledge:  star,
          speed_of_service:      star,
          pricing_rating:        Math.max(1, star - 1),
          communication_rating:  star,
          comments:              `Rated ${star}/5 from dashboard`,
        });
      }
      setFeedbackDone(true);
    } catch (e) { setFeedbackDone(true); }
  }

  // ── NEW: Download vehicle RCA/CAPA PDF ────────────────────
  async function downloadManufacturingPdf() {
    setDownloadingPdf(true);
    try {
      const API = import.meta.env.VITE_API_URL || "http://192.168.249.221:8000";
      const response = await fetch(`${API}/manufacturing/pdf/${id}`, {
        headers: { "ngrok-skip-browser-warning": "true" },
      });
      if (!response.ok) throw new Error("PDF generation failed");
      const blob = await response.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `RCA_CAPA_${id}_${new Date().toISOString().slice(0, 10)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("PDF download failed: " + e.message);
    } finally {
      setDownloadingPdf(false);
    }
  }

  // ── NEW: Download fleet-wide PDF ──────────────────────────
  async function downloadFleetPdf() {
    setDownloadingFleetPdf(true);
    try {
      const API = import.meta.env.VITE_API_URL || "http://192.168.249.221:8000";
      const response = await fetch(`${API}/manufacturing/pdf/fleet`, {
        headers: { "ngrok-skip-browser-warning": "true" },
      });
      if (!response.ok) throw new Error("Fleet PDF failed");
      const blob = await response.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `Fleet_RCA_CAPA_${new Date().toISOString().slice(0, 10)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Fleet PDF failed: " + e.message);
    } finally {
      setDownloadingFleetPdf(false);
    }
  }

  // ─────────────────────────────────────────────────────────
  if (loading) return (
    <div className="pt-14 min-h-screen flex items-center justify-center text-white/50">
      Loading {id}...
    </div>
  );
  if (!vehicle) return (
    <div className="pt-14 min-h-screen flex items-center justify-center text-red-400">
      Vehicle {id} not found
    </div>
  );

  const color = statusColor(vehicle.status);
  const s     = vehicle.sensors;
  const eng   = analysis?.findings?.EngagementAgent;

  const gauges = [
    { name: "Brake Temp",   value: s.brakeTemp,   max: 130, unit: "°C",   danger: s.brakeTemp > 100  },
    { name: "Engine Temp",  value: s.engineTemp,  max: 120, unit: "°C",   danger: s.engineTemp > 105 },
    { name: "Oil Pressure", value: s.oilPressure, max: 80,  unit: " PSI", danger: s.oilPressure < 25 },
    { name: "Brake Fluid",  value: s.brakeFluid,  max: 100, unit: "%",    danger: s.brakeFluid < 65  },
  ];

  return (
    <div className="pt-14 min-h-screen p-5" style={{ background: "transparent" }}>
      <style>{`@keyframes slideIn{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}`}</style>

      {/* Back button */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-2 text-white/40 text-sm mb-5 hover:text-white/70 transition-colors"
      >
        ← Back to Dashboard
      </button>

      {/* ── Vehicle Header ─────────────────────────────────── */}
      <div className="bg-gray-900 border border-white/5 rounded-xl p-5 mb-5">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-xs text-white/30 font-mono mb-1">{vehicle.id}</div>
            <h1 className="text-2xl font-bold text-white">{vehicle.name}</h1>
            <div className="text-sm text-white/40 mt-1">
              👤 {vehicle.owner_name} · 📱 {vehicle.owner_phone} · ✉️ {vehicle.owner_email}
            </div>
          </div>
          <span className="text-xs font-bold px-3 py-1.5 rounded-full uppercase"
            style={{ background: color + "20", color }}>
            {vehicle.status === "critical" ? "🔴 CRITICAL"
              : vehicle.status === "warning" ? "🟡 WARNING"
              : "🟢 HEALTHY"}
          </span>
        </div>

        {/* Quick sensor summary */}
        <div className="flex gap-8 mt-4 pt-4 border-t border-white/5 flex-wrap">
          {[
            { label: "Mileage",     value: vehicle.mileage?.toLocaleString() + " km", color: null },
            { label: "Brake Temp",  value: s.brakeTemp   + "°C",   color: s.brakeTemp   > 100 ? "#ff4560" : "#00e396" },
            { label: "Oil Press",   value: s.oilPressure + " PSI", color: s.oilPressure < 25  ? "#ff4560" : "#00e396" },
            { label: "Engine",      value: s.engineTemp  + "°C",   color: s.engineTemp  > 105 ? "#ff4560" : "#00e396" },
            { label: "Brake Fluid", value: s.brakeFluid  + "%",    color: s.brakeFluid  < 65  ? "#ff4560" : "#00e396" },
          ].map(m => (
            <div key={m.label}>
              <div className="text-xs text-white/30">{m.label}</div>
              <div className="text-sm font-bold mt-0.5" style={{ color: m.color || "white" }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* Notification status row — appears after analysis */}
        {eng && (
          <div className="mt-4 pt-3 border-t border-white/5 flex flex-wrap gap-3 text-xs">
            <span className={eng.sms_sent   ? "text-green-400" : "text-red-400"}>
              {eng.sms_sent   ? "✅ SMS Sent"   : "❌ SMS Failed"}
            </span>
            <span className={eng.email_sent ? "text-green-400" : "text-red-400"}>
              {eng.email_sent ? "✅ Email Sent" : "❌ Email Failed"}
            </span>
            <span className={eng.call_action === "call_now" ? "text-blue-400" : "text-yellow-400"}>
              {eng.call_action === "call_now"
                ? `📞 Called — ${eng.call_outcome}`
                : `⏰ Call scheduled at 9:00 AM`}
            </span>
          </div>
        )}
      </div>

      {/* ── 2-column layout ────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-5">

        {/* ── LEFT: Sensors + Booking + PDF ──────────────── */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-bold text-sm text-white">Live Sensors</h2>
            <span className="text-xs bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2 py-0.5 rounded-full">
              {vehicle.id}
            </span>
          </div>

          {/* Sensor gauges */}
          {gauges.map(g => {
            const pct = Math.min(100, Math.round((g.value / g.max) * 100));
            const gc  = g.danger ? "#ff4560" : "#00e396";
            return (
              <div key={g.name} className="mb-4">
                <div className="flex justify-between items-baseline mb-1.5">
                  <span className="text-xs text-white/50">{g.name}</span>
                  <span className="text-sm font-black" style={{ color: gc }}>{g.value}{g.unit}</span>
                </div>
                <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-700"
                    style={{ width: pct + "%", background: gc }} />
                </div>
                {g.danger && (
                  <div className="text-xs text-red-400 mt-1">⚠️ Abnormal reading</div>
                )}
              </div>
            );
          })}

          {/* Mileage row */}
          <div className="mt-2 pt-3 border-t border-white/5 flex justify-between">
            <span className="text-xs text-white/40">Mileage</span>
            <span className="text-sm font-bold text-white">{vehicle.mileage?.toLocaleString()} km</span>
          </div>

          {/* Book Service button */}
          <button
            onClick={() => setShowBooking(true)}
            className="mt-4 w-full py-2 rounded-xl text-xs font-bold transition-all hover:opacity-80"
            style={{
              background: "rgba(0,227,150,0.12)",
              border:     "1px solid rgba(0,227,150,0.3)",
              color:      "#00e396",
            }}
          >
            📅 Book Service
          </button>

          {/* Booking confirmation */}
          {bookingResult && (
            <div className="mt-3 p-3 bg-green-500/10 border border-green-500/30 rounded-xl text-xs text-green-300">
              ✅ Booked! ID: {bookingResult.booking_id}<br />
              {bookingResult.service_date} at {bookingResult.service_time}
            </div>
          )}

          {/* Feedback stars */}
          {bookingResult && !feedbackDone && (
            <div className="mt-3 p-3 bg-yellow-500/5 border border-yellow-500/20 rounded-xl">
              <div className="text-xs text-yellow-400 font-bold mb-2">⭐ Rate your service</div>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map(star => (
                  <button
                    key={star}
                    onClick={() => handleFeedback(star)}
                    className={`text-xl hover:scale-125 transition-transform ${feedbackStar >= star ? "opacity-100" : "opacity-40"}`}
                  >
                    ⭐
                  </button>
                ))}
              </div>
            </div>
          )}
          {feedbackDone && (
            <div className="mt-3 p-2 rounded-xl bg-green-500/10 border border-green-500/20 text-xs text-green-400 text-center">
              ✅ Thank you! 5% discount applied.
            </div>
          )}

          {/* ── PDF Download Buttons ─────────────────────── */}
          <div className="mt-4 pt-3 border-t border-white/5 space-y-2">
            <div className="text-xs text-white/30 uppercase tracking-wide mb-2">
              Download Reports
            </div>

            {/* Vehicle RCA/CAPA PDF */}
            <button
              onClick={downloadManufacturingPdf}
              disabled={downloadingPdf}
              className="w-full py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 hover:opacity-80"
              style={{
                background: downloadingPdf
                  ? "rgba(255,255,255,0.05)"
                  : "rgba(168,85,247,0.15)",
                border: `1px solid ${downloadingPdf
                  ? "rgba(255,255,255,0.1)"
                  : "rgba(168,85,247,0.4)"}`,
                color: downloadingPdf
                  ? "rgba(255,255,255,0.3)"
                  : "#a855f7",
                cursor: downloadingPdf ? "not-allowed" : "pointer",
              }}
            >
              {downloadingPdf ? "⏳ Generating PDF..." : "📄 Download RCA/CAPA Report"}
            </button>

            {/* Fleet-wide PDF */}
            <button
              onClick={downloadFleetPdf}
              disabled={downloadingFleetPdf}
              className="w-full py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 hover:opacity-80"
              style={{
                background: downloadingFleetPdf
                  ? "rgba(255,255,255,0.05)"
                  : "rgba(59,130,246,0.15)",
                border: `1px solid ${downloadingFleetPdf
                  ? "rgba(255,255,255,0.1)"
                  : "rgba(59,130,246,0.4)"}`,
                color: downloadingFleetPdf
                  ? "rgba(255,255,255,0.3)"
                  : "#60a5fa",
                cursor: downloadingFleetPdf ? "not-allowed" : "pointer",
              }}
            >
              {downloadingFleetPdf ? "⏳ Generating..." : "📊 Download Fleet Report PDF"}
            </button>
          </div>
        </div>

        {/* ── RIGHT: AI Analysis ─────────────────────────── */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-bold text-sm text-white">🤖 AI Agent Analysis</h2>
            <button
              onClick={runAnalysis}
              disabled={analyzing}
              className="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
              style={{
                background: analyzing ? "rgba(255,255,255,0.05)" : "rgba(0,229,255,0.12)",
                border:     `1px solid ${analyzing ? "rgba(255,255,255,0.1)" : "rgba(0,229,255,0.3)"}`,
                color:      analyzing ? "rgba(255,255,255,0.3)" : "#00e5ff",
                cursor:     analyzing ? "not-allowed" : "pointer",
              }}
            >
              {analyzing ? "⏳ Analyzing..." : "🔍 Run Full Analysis"}
            </button>
          </div>

          {/* Agent pill chips — show while analyzing or after done */}
          {(analyzing || done) && (
            <div className="flex flex-wrap gap-1.5 mb-4 p-3 bg-gray-800 rounded-xl">
              {AGENT_CONFIG.map(a => (
                <div
                  key={a.key}
                  className="text-xs px-2.5 py-1 rounded-full font-bold transition-all"
                  style={{
                    background: currentAgent === a.key
                      ? "rgba(255,170,0,0.2)"
                      : visibleAgents.includes(a.key)
                        ? "rgba(0,227,150,0.15)"
                        : "rgba(255,255,255,0.05)",
                    color: currentAgent === a.key
                      ? "#ffaa00"
                      : visibleAgents.includes(a.key)
                        ? "#00e396"
                        : "rgba(255,255,255,0.25)",
                    border: `1px solid ${currentAgent === a.key
                      ? "rgba(255,170,0,0.3)"
                      : visibleAgents.includes(a.key)
                        ? "rgba(0,227,150,0.2)"
                        : "rgba(255,255,255,0.05)"}`,
                  }}
                >
                  {a.icon} {a.name}
                </div>
              ))}
            </div>
          )}

          {/* Staggered agent result cards */}
          {visibleAgents.length > 0 && analysis && (
            <div className="flex flex-col gap-2 max-h-96 overflow-y-auto pr-1">
              {AGENT_CONFIG
                .filter(a => visibleAgents.includes(a.key))
                .map(a => (
                  <AgentResultCard
                    key={a.key}
                    agentKey={a.key}
                    config={a}
                    finding={analysis.findings?.[a.key]}
                    vehicle={vehicle}
                  />
                ))}
            </div>
          )}

          {/* Final summary banner */}
          {done && analysis && (
            <div
              className="mt-3 p-3 rounded-xl text-center"
              style={{
                background: vehicle.status === "critical"
                  ? "rgba(255,69,96,0.08)"
                  : vehicle.status === "warning"
                    ? "rgba(255,170,0,0.08)"
                    : "rgba(0,227,150,0.08)",
                border: `1px solid ${color}30`,
              }}
            >
              <div className="text-sm font-bold" style={{ color }}>
                {vehicle.status === "critical"
                  ? "🚨 URGENT ACTION REQUIRED"
                  : vehicle.status === "warning"
                    ? "⚠️ MAINTENANCE NEEDED"
                    : "✅ VEHICLE HEALTHY"}
              </div>
              <div className="text-xs text-white/40 mt-1">
                {analysis.final_assessment?.summary}
              </div>
              {eng?.call_outcome === "appointment_booked" && (
                <div className="text-xs text-green-400 mt-1">
                  ✅ Appointment booked during call!
                </div>
              )}
            </div>
          )}

          {/* Empty state */}
          {visibleAgents.length === 0 && !analyzing && (
            <div className="text-center py-10 text-white/25 text-sm">
              <div className="text-3xl mb-3">🤖</div>
              Click "Run Full Analysis"<br />
              <span className="text-xs">8 AI agents · real voice call · SMS · scheduling</span>
            </div>
          )}
        </div>
      </div>

      {/* ── Booking modal ───────────────────────────────── */}
      {showBooking && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 w-80">
            <h3 className="font-bold text-white mb-4">Book Emergency Service</h3>
            <p className="text-white/50 text-sm mb-4">
              Vehicle: {vehicle.id} — {vehicle.name}<br />
              Date: Tomorrow · Time: 9:00 AM
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleBook}
                className="flex-1 py-2 bg-green-600 hover:bg-green-700 rounded-xl text-white text-sm font-bold transition-colors"
              >
                ✅ Confirm
              </button>
              <button
                onClick={() => setShowBooking(false)}
                className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded-xl text-white text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
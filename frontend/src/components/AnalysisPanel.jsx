import { useState } from "react";
import { analyzeVehicle, mlPredict } from "../services/api";

export default function AnalysisPanel({ vehicle }) {
  const [result,   setResult]   = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  if (!vehicle) return null;

  // ── Analyze button click ──
  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeVehicle(vehicle.id);
      setResult(data);
    } catch (err) {
      setError("Unable to connect to the backend. Mock data is being displayed.");
      // Mock result for demo
      setResult({
        vehicle_id: vehicle.id,
        final_assessment: {
          overall_status: "needs_attention",
          priority: "HIGH",
          recommended_action: "Service within 7 days",
        },
        findings: {
          data_analysis: {
            anomalies: ["brake_temp_high"],
            severity: "HIGH",
          },
          diagnosis: {
            prediction: "FAILURE",
            probability: 85,
            risk_level: "HIGH",
            estimated_days: 7,
          },
          engagement: {
            message: "URGENT: Vehicle requires immediate attention",
            channel: "SMS + Email",
            should_notify_now: true,
          },
          scheduling: {
            urgency: "EMERGENCY",
            scheduled_date: "Tomorrow 9:00 AM",
            duration: "2 hours",
          },
        },
      });
    }
    setLoading(false);
  }

  const sc = {
    critical:       "#ff2d55",
    warning:        "#ffb800",
    healthy:        "#00ff9d",
    HIGH:           "#ff2d55",
    MEDIUM:         "#ffb800",
    LOW:            "#00ff9d",
    needs_attention:"#ffb800",
    good:           "#00ff9d",
  };

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">
          🤖 AI Analysis — {vehicle.id}
        </h2>
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="px-4 py-1.5 rounded-lg text-xs font-bold transition-all"
          style={{
            background: loading
              ? "rgba(255,255,255,0.05)"
              : "rgba(0,229,255,0.12)",
            border: `1px solid ${loading
              ? "rgba(255,255,255,0.1)"
              : "rgba(0,229,255,0.3)"}`,
            color: loading ? "rgba(255,255,255,0.3)" : "#00e5ff",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "⏳ Analyzing..." : "🔍 Run Full Analysis"}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="text-xs text-amber-400 bg-amber-500/10
                        border border-amber-500/20 rounded-lg p-2 mb-3">
          ⚠️ {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="text-center py-8">
          <div className="text-2xl mb-2">⚙️</div>
          <div className="text-xs text-white/40">
            8 AI agents analyzing {vehicle.id}...
          </div>
          <div className="flex justify-center gap-1 mt-3">
            {["Data","Diagnosis","Engagement","Scheduling"].map((a,i) => (
              <div key={i}
                className="text-xs px-2 py-1 rounded-full"
                style={{
                  background: "rgba(0,229,255,0.08)",
                  color: "#00e5ff",
                  animation: `pulse ${1+i*0.2}s infinite`,
                }}>
                {a}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="flex flex-col gap-3">

          {/* Final Assessment */}
          <div className="bg-gray-800 rounded-xl p-3">
            <div className="text-xs text-white/40 mb-2 font-bold tracking-widest">
              FINAL ASSESSMENT
            </div>
            <div className="flex gap-4">
              <div>
                <div className="text-xs text-white/40">Status</div>
                <div className="text-sm font-bold mt-0.5"
                  style={{ color: sc[result.final_assessment?.overall_status] || "#ffb800" }}>
                  {result.final_assessment?.overall_status?.toUpperCase() || "N/A"}
                </div>
              </div>
              <div>
                <div className="text-xs text-white/40">Priority</div>
                <div className="text-sm font-bold mt-0.5"
                  style={{ color: sc[result.final_assessment?.priority] || "#ffb800" }}>
                  {result.final_assessment?.priority || "N/A"}
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-white/40">Action</div>
                <div className="text-sm font-semibold text-white mt-0.5">
                  {result.final_assessment?.recommended_action || "N/A"}
                </div>
              </div>
            </div>
          </div>

          {/* Agent Results */}
          {result.findings && (
            <div className="flex flex-col gap-2">

              {/* Data Analysis */}
              {result.findings.data_analysis && (
                <div className="bg-gray-800 rounded-xl p-3 border-l-2"
                  style={{ borderLeftColor: sc[result.findings.data_analysis.severity] || "#ffb800" }}>
                  <div className="text-xs text-white/40 mb-1">📊 DATA ANALYSIS AGENT</div>
                  <div className="text-xs text-white/70">
                    Severity: <span className="font-bold"
                      style={{ color: sc[result.findings.data_analysis.severity] }}>
                      {result.findings.data_analysis.severity}
                    </span>
                  </div>
                  {result.findings.data_analysis.anomalies?.length > 0 && (
                    <div className="text-xs text-white/50 mt-1">
                      Issues: {result.findings.data_analysis.anomalies.join(", ")}
                    </div>
                  )}
                </div>
              )}

              {/* Diagnosis */}
              {result.findings.diagnosis && (
                <div className="bg-gray-800 rounded-xl p-3 border-l-2"
                  style={{ borderLeftColor: sc[result.findings.diagnosis.risk_level] || "#ffb800" }}>
                  <div className="text-xs text-white/40 mb-1">🔬 DIAGNOSIS AGENT</div>
                  <div className="flex gap-4">
                    <div>
                      <div className="text-xs text-white/40">Probability</div>
                      <div className="text-lg font-black"
                        style={{ color: sc[result.findings.diagnosis.risk_level] }}>
                        {result.findings.diagnosis.probability}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40">Risk</div>
                      <div className="text-sm font-bold mt-0.5"
                        style={{ color: sc[result.findings.diagnosis.risk_level] }}>
                        {result.findings.diagnosis.risk_level}
                      </div>
                    </div>
                    {result.findings.diagnosis.estimated_days && (
                      <div>
                        <div className="text-xs text-white/40">Days Left</div>
                        <div className="text-sm font-bold text-red-400 mt-0.5">
                          {result.findings.diagnosis.estimated_days}d
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Engagement */}
              {result.findings.engagement && (
                <div className="bg-gray-800 rounded-xl p-3 border-l-2 border-purple-500/50">
                  <div className="text-xs text-white/40 mb-1">📞 ENGAGEMENT AGENT</div>
                  <div className="text-xs text-white/70 mb-1">
                    {result.findings.engagement.message}
                  </div>
                  <div className="flex gap-2 items-center">
                    <span className="text-xs bg-purple-500/10 text-purple-400
                                     border border-purple-500/20 px-2 py-0.5 rounded-full">
                      {result.findings.engagement.channel}
                    </span>
                    {result.findings.engagement.should_notify_now && (
                      <span className="text-xs bg-green-500/10 text-green-400
                                       border border-green-500/20 px-2 py-0.5 rounded-full">
                        ✅ Notification Sent
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Scheduling */}
              {result.findings.scheduling && (
                <div className="bg-gray-800 rounded-xl p-3 border-l-2 border-cyan-500/40">
                  <div className="text-xs text-white/40 mb-1">📅 SCHEDULING AGENT</div>
                  <div className="flex gap-4">
                    <div>
                      <div className="text-xs text-white/40">Appointment</div>
                      <div className="text-sm font-bold text-cyan-400 mt-0.5">
                        {result.findings.scheduling.scheduled_date}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-white/40">Duration</div>
                      <div className="text-sm font-semibold text-white mt-0.5">
                        {result.findings.scheduling.duration}
                      </div>
                    </div>
                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      )}

      {/* Default state */}
      {!result && !loading && (
        <div className="text-center py-6 text-white/25 text-sm">
          "Run Full Analysis" click karo — 8 AI agents analyze karenge
        </div>
      )}

    </div>
  );
}

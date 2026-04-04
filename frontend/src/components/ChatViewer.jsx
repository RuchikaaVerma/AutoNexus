import { useState, useEffect } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_URL || "http://192.168.249.221:8000";

// Default demo messages (shown before real analysis runs)
const DEFAULT_MESSAGES = [
  {
    role: "ai",
    who:  "Sarah (AI Agent)",
    time: "—",
    text: "Run AI Analysis on any vehicle to see real engagement conversation here.",
  },
];

export default function ChatViewer() {
  const [messages,    setMessages]    = useState(DEFAULT_MESSAGES);
  const [vehicleInfo, setVehicleInfo] = useState(null);
  const [bookingInfo, setBookingInfo] = useState(null);
  const [status,      setStatus]      = useState("idle"); // idle | booked | pending

  // Listen for analysis events via custom event (fired from VehicleDetail)
  useEffect(() => {
    function handleAnalysis(e) {
      const { analysis, vehicle } = e.detail || {};
      if (!analysis) return;

      const eng   = analysis.findings?.EngagementAgent;
      const sched = analysis.findings?.SchedulingAgent;

      if (!eng) return;

      const newMessages = [];
      const now = new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });

      // Sarah's opening message
      const issues = eng.issues_detected?.join(", ") || "vehicle issues";
      newMessages.push({
        role: "ai",
        who:  "Sarah (AI Agent)",
        time: now,
        text: `Hello ${vehicle?.owner_name || "there"}! This is Sarah from AutoNexus. Our AI has detected critical issues with your ${vehicle?.model || "vehicle"}: ${issues}. ${eng.is_business_hours ? "Shall I book an emergency service appointment?" : "I'll call you at 9 AM. Sending details by SMS now."}`,
      });

      // Customer response (simulated from call outcome)
      if (eng.call_outcome === "appointment_booked") {
        newMessages.push({
          role: "human",
          who:  vehicle?.owner_name || "Owner",
          time: now,
          text: "Yes please — book the earliest available slot.",
        });
        newMessages.push({
          role: "ai",
          who:  "Sarah (AI Agent)",
          time: now,
          text: `Perfect! I've booked your appointment at ${sched?.shop_details?.name || sched?.appointment?.service_center || "AutoNexus Central"} on ${sched?.appointment?.date || "tomorrow"} at ${sched?.appointment?.time_slot || sched?.appointment?.time || "9:00 AM"}. Confirmation SMS sent! 🎉`,
        });
        setStatus("booked");
        setBookingInfo(sched?.appointment);
      } else if (eng.call_action === "call_at_9am") {
        newMessages.push({
          role: "ai",
          who:  "Sarah (AI Agent)",
          time: now,
          text: `It's currently ${eng.current_hour}:00 — outside business hours. SMS and email sent now. I'll call you at 9:00 AM tomorrow to schedule service. 🌙`,
        });
        setStatus("pending");
      } else if (eng.call_outcome === "no_response") {
        newMessages.push({
          role: "ai",
          who:  "Sarah (AI Agent)",
          time: now,
          text: "Unable to reach owner by phone. SMS and email sent with full details and booking link.",
        });
        setStatus("pending");
      } else {
        setStatus("idle");
      }

      setMessages(newMessages);
      setVehicleInfo(vehicle);
    }

    window.addEventListener("autonexus_analysis", handleAnalysis);
    return () => window.removeEventListener("autonexus_analysis", handleAnalysis);
  }, []);

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">Customer Engagement</h2>
        <span className={`text-xs px-2 py-0.5 rounded-full font-semibold border ${
          status === "booked"
            ? "bg-green-500/10 text-green-400 border-green-500/20"
            : status === "pending"
            ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
            : "bg-gray-500/10 text-gray-400 border-gray-500/20"
        }`}>
          {status === "booked" ? "✅ Booked" : status === "pending" ? "⏰ Pending" : "○ Waiting"}
        </span>
      </div>

      {/* Vehicle info */}
      {vehicleInfo && (
        <div className="bg-gray-800 rounded-lg px-3 py-2 mb-3 flex items-center gap-2">
          <span className="text-base">🚗</span>
          <div>
            <div className="text-xs font-semibold text-white">
              {vehicleInfo.id} — {vehicleInfo.model}
            </div>
            <div className="text-xs text-white/40">{vehicleInfo.owner_name}</div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex flex-col gap-2 mb-3 max-h-48 overflow-y-auto">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "human" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-xs text-xs rounded-xl px-3 py-2 ${
              m.role === "ai"
                ? "bg-cyan-500/8 border border-cyan-500/15 rounded-tl-sm"
                : "bg-purple-500/8 border border-purple-500/15 rounded-tr-sm"
            }`}>
              <div className="text-white/30 mb-1">{m.who} · {m.time}</div>
              <div className="text-white/80 leading-relaxed">{m.text}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Appointment confirmation */}
      {bookingInfo ? (
        <div className="bg-green-500/5 border border-green-500/15 rounded-lg p-2.5 text-xs text-green-400 text-center font-semibold">
          📅 {bookingInfo.date} · {bookingInfo.time_slot || bookingInfo.time} · {bookingInfo.service_center || "AutoNexus Central"}
          {bookingInfo.shop_address && (
            <div className="text-green-400/60 font-normal mt-1">
              📍 {bookingInfo.shop_address}
            </div>
          )}
          {bookingInfo.shop_phone && (
            <div className="text-green-400/60 font-normal">
              📞 {bookingInfo.shop_phone}
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-800/50 border border-white/5 rounded-lg p-2.5 text-xs text-white/30 text-center">
          {status === "pending"
            ? "⏰ Call scheduled for 9:00 AM"
            : "Run analysis on a vehicle to see conversation"}
        </div>
      )}
    </div>
  );
}

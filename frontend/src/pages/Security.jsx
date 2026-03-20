import { motion } from "framer-motion";

const log = [
  {
    level:  "ok",
    score:  5,
    agent:  "Data Analysis Agent",
    event:  "Sensor Read — VEH001 to VEH010",
    detail: "10 records accessed · Normal behavior · 9:00:15 AM",
    time:   "09:00",
  },
  {
    level:  "ok",
    score:  8,
    agent:  "Diagnosis Agent",
    event:  "ML Prediction Generated",
    detail: "VEH001 brake prediction · Model v2.3 · 9:00:22 AM",
    time:   "09:00",
  },
  {
    level:  "ok",
    score:  12,
    agent:  "Engagement Agent",
    event:  "Customer Contacted — Sarah Khan",
    detail: "WhatsApp message sent · Appointment confirmed · 9:03 AM",
    time:   "09:03",
  },
  {
    level:  "warn",
    score:  65,
    agent:  "Engagement Agent",
    event:  "⚠️ Unusual Activity Hour",
    detail: "Activity at 3:15 AM · Outside baseline 9AM–8PM · Monitored",
    time:   "03:15",
  },
  {
    level:  "critical",
    score:  92,
    agent:  "Scheduling Agent",
    event:  "🚫 BLOCKED — Unauthorized Data Access",
    detail: "Tried to read vehicle sensor data · No permission · Admin alerted",
    time:   "02:44",
  },
];

const style = {
  ok: {
    border: "#00e396",
    bg:     "rgba(0,227,150,0.05)",
    text:   "#00e396",
    badge:  "rgba(0,227,150,0.12)",
  },
  warn: {
    border: "#ffaa00",
    bg:     "rgba(255,170,0,0.05)",
    text:   "#ffaa00",
    badge:  "rgba(255,170,0,0.12)",
  },
  critical: {
    border: "#ff4560",
    bg:     "rgba(255,69,96,0.05)",
    text:   "#ff4560",
    badge:  "rgba(255,69,96,0.12)",
  },
};

export default function Security() {
  const blocked  = log.filter(l => l.level === "critical").length;
  const warnings = log.filter(l => l.level === "warn").length;
  const normal   = log.filter(l => l.level === "ok").length;

  return (
    <div className="pt-16 min-h-screen bg-gray-950 p-5
                    max-w-4xl mx-auto">

      {/* PAGE TITLE */}
      <div className="mb-6">
        <p className="text-xs text-white/30 tracking-widest uppercase mb-1">
          UEBA Monitor
        </p>
        <h1 className="text-2xl font-bold text-white">
          Security Intelligence
        </h1>
      </div>

      {/* ── STATUS HERO ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-green-500/5 border border-green-500/20
                   rounded-xl p-5 flex items-center gap-5 mb-6"
      >
        <span className="text-5xl">🛡️</span>
        <div>
          <div className="text-lg font-bold text-green-400">
            System Secure
          </div>
          <div className="text-sm text-white/40 mt-0.5">
            All 7 agents operating within behavioral baselines
          </div>
        </div>

        {/* Stats */}
        <div className="ml-auto flex gap-6 text-center">
          <div>
            <div className="text-2xl font-black text-green-400">
              847
            </div>
            <div className="text-xs text-white/30 mt-1">
              Monitored
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-amber-400">
              {warnings}
            </div>
            <div className="text-xs text-white/30 mt-1">
              Flagged
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-red-400">
              {blocked}
            </div>
            <div className="text-xs text-white/30 mt-1">
              Blocked
            </div>
          </div>
          <div>
            <div className="text-2xl font-black text-cyan-400">
              {normal}
            </div>
            <div className="text-xs text-white/30 mt-1">
              Normal
            </div>
          </div>
        </div>
      </motion.div>

      {/* ── ACTIVITY LOG ── */}
      <div className="bg-gray-900 border border-white/5 rounded-xl p-5">

        <div className="flex justify-between items-center mb-5">
          <h2 className="font-bold text-sm text-white">
            Activity Log — Today
          </h2>
          <span className="text-xs bg-cyan-500/10 text-cyan-400
                           border border-cyan-500/20
                           px-3 py-1 rounded-full">
            847 events
          </span>
        </div>

        <div className="flex flex-col gap-2">
          {log.map((l, i) => {
            const s = style[l.level];
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex items-start gap-4 p-3
                           rounded-xl border-l-2
                           hover:brightness-110 transition-all"
                style={{
                  borderLeftColor: s.border,
                  background:      s.bg,
                }}
              >
                {/* Time */}
                <div className="text-xs text-white/25 font-mono
                                pt-0.5 w-10 flex-shrink-0">
                  {l.time}
                </div>

                {/* Info */}
                <div className="flex-1">
                  <div className="text-xs text-white/40 mb-0.5">
                    {l.agent}
                  </div>
                  <div className="text-sm font-semibold text-white">
                    {l.event}
                  </div>
                  <div className="text-xs text-white/40 mt-0.5">
                    {l.detail}
                  </div>
                </div>

                {/* Score badge */}
                <span
                  className="text-xs font-black px-2.5 py-1
                             rounded-full whitespace-nowrap flex-shrink-0"
                  style={{
                    background: s.badge,
                    color:      s.text,
                  }}
                >
                  Score {l.score}
                </span>
              </motion.div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
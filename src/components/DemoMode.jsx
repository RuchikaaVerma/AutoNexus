import { useState, useEffect, useRef } from "react";

// Demo script — kya kya hoga aur kab
const DEMO_STEPS = [
  {
    time: 0,
    agent: null,
    toast: "🔍 System scanning all 10 vehicles...",
    color: "#00c8ff",
  },
  {
    time: 2500,
    agent: "data",
    toast: "📊 Data Analysis Agent — VEH001 brake temp anomaly detected!",
    color: "#ffaa00",
  },
  {
    time: 5500,
    agent: "diagnosis",
    toast: "🔬 Diagnosis Agent — Brake failure predicted in 7 days (85%)",
    color: "#ff7700",
  },
  {
    time: 8500,
    agent: "engagement",
    toast: "📞 Engagement Agent — Contacting Sarah Khan...",
    color: "#a855f7",
  },
  {
    time: 12000,
    agent: "scheduling",
    toast: "📅 Scheduling Agent — Appointment booked! Wednesday 9AM ✅",
    color: "#00e396",
  },
  {
    time: 15500,
    agent: "manufacturing",
    toast: "🏭 Manufacturing Agent — Brake pad defect pattern logged",
    color: "#00c8ff",
  },
  {
    time: 18500,
    agent: null,
    toast: "✅ Full cycle complete — Breakdown prevented, ₹15,000 saved!",
    color: "#00e396",
  },
];

export default function DemoMode({ onAgentChange }) {
  const [running, setRunning]   = useState(false);
  const [toast, setToast]       = useState(null);
  const [toastColor, setToastColor] = useState("#00c8ff");
  const [step, setStep]         = useState(0);
  const timers = useRef([]);

  // Demo shuru karo
  function startDemo() {
    // Purane timers clear karo
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setRunning(true);
    setStep(0);

    DEMO_STEPS.forEach((s, i) => {
      const t = setTimeout(() => {
        // Toast dikhao
        setToast(s.toast);
        setToastColor(s.color);
        setStep(i);

        // Agent highlight karo
        if (s.agent && onAgentChange) {
          onAgentChange(s.agent);
        }

        // Last step — demo khatam
        if (i === DEMO_STEPS.length - 1) {
          setTimeout(() => {
            setRunning(false);
            setToast(null);
            if (onAgentChange) onAgentChange(null);
          }, 3000);
        }
      }, s.time);

      timers.current.push(t);
    });
  }

  // Demo band karo
  function stopDemo() {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setRunning(false);
    setToast(null);
    if (onAgentChange) onAgentChange(null);
  }

  // Component unmount pe cleanup
  useEffect(() => {
    return () => timers.current.forEach(clearTimeout);
  }, []);

  return (
    <>
      {/* ── TOAST NOTIFICATION ── */}
      {toast && (
        <div
          className="fixed top-20 left-1/2 z-50
                     px-6 py-3 rounded-full text-sm font-semibold
                     border backdrop-blur-md
                     transition-all duration-300"
          style={{
            transform: "translateX(-50%)",
            background: toastColor + "15",
            borderColor: toastColor + "40",
            color: toastColor,
            boxShadow: `0 4px 24px ${toastColor}20`,
          }}
        >
          {toast}
        </div>
      )}

      {/* ── DEMO BUTTON ── */}
      <button
        onClick={running ? stopDemo : startDemo}
        className="fixed bottom-6 right-6 z-50
                   flex items-center gap-2
                   px-5 py-3 rounded-full
                   font-semibold text-sm
                   border transition-all duration-200
                   hover:-translate-y-0.5"
        style={{
          background: running
            ? "rgba(255,69,96,0.1)"
            : "rgba(0,200,255,0.1)",
          borderColor: running
            ? "rgba(255,69,96,0.3)"
            : "rgba(0,200,255,0.3)",
          color: running ? "#ff4560" : "#00c8ff",
          boxShadow: running
            ? "0 4px 20px rgba(255,69,96,0.15)"
            : "0 4px 20px rgba(0,200,255,0.15)",
        }}
      >
        {/* Icon */}
        <span className="text-base">
          {running ? "⏹" : "▶"}
        </span>

        {/* Text */}
        <span>
          {running ? "Stop Demo" : "▶ Run Demo"}
        </span>

        {/* Running indicator */}
        {running && (
          <span
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ background: "#ff4560" }}
          />
        )}
      </button>
    </>
  );
}
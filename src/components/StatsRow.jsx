import { motion } from "framer-motion";

export default function StatsRow({ stats }) {
  // ── Safety: works with BOTH old mockData shape AND new backend shape ──
  // Old shape: { total, alerts, healthy, accuracy, moneySaved }
  // New shape: array of { label, value, ... } OR backend stats object

  let items;

  if (Array.isArray(stats)) {
    // New shape — already mapped in Dashboard.jsx
    items = stats.map((s, i) => ({
      label: s.label,
      value: s.suffix ? `${s.prefix || ""}${s.value}${s.suffix}` : String(s.value ?? 0),
      color: s.color
        ? s.color === "#ff4560" ? "text-red-400"
        : s.color === "#ffaa00" ? "text-amber-400"
        : s.color === "#00e396" ? "text-green-400"
        : "text-cyan-400"
        : ["text-cyan-400","text-red-400","text-amber-400","text-green-400","text-purple-400"][i % 5],
      bg: s.color
        ? s.color === "#ff4560" ? "bg-red-500/10"
        : s.color === "#ffaa00" ? "bg-amber-500/10"
        : s.color === "#00e396" ? "bg-green-500/10"
        : "bg-cyan-500/10"
        : ["bg-cyan-500/10","bg-red-500/10","bg-amber-500/10","bg-green-500/10","bg-purple-500/10"][i % 5],
      icon: s.icon || "📊",
    }));
  } else if (stats && typeof stats === "object") {
    // Old mockData shape — map manually
    const total      = stats.total      ?? stats.total_vehicles ?? 10;
    const alerts     = stats.alerts     ?? stats.status_distribution?.critical ?? 0;
    const healthy    = stats.healthy    ?? stats.status_distribution?.healthy  ?? 0;
    const accuracy   = stats.accuracy   ?? 94;
    const moneySaved = stats.moneySaved ?? (healthy * 1000);

    items = [
      { label: "Total Vehicles",   value: String(total),         color: "text-cyan-400",   bg: "bg-cyan-500/10",   icon: "🚗" },
      { label: "Active Alerts",    value: String(alerts),        color: "text-red-400",    bg: "bg-red-500/10",    icon: "🚨" },
      { label: "Healthy",          value: String(healthy),       color: "text-green-400",  bg: "bg-green-500/10",  icon: "✅" },
      { label: "Model Accuracy",   value: `${accuracy}%`,        color: "text-amber-400",  bg: "bg-amber-500/10",  icon: "🎯" },
      { label: "Breakdowns Saved", value: `₹${Math.floor((moneySaved || 0) / 1000)}K`, color: "text-purple-400", bg: "bg-purple-500/10", icon: "💰" },
    ];
  } else {
    // No data yet — show loading placeholders
    items = [
      { label: "Total Vehicles",   value: "—", color: "text-cyan-400",   bg: "bg-cyan-500/10",   icon: "🚗" },
      { label: "Active Alerts",    value: "—", color: "text-red-400",    bg: "bg-red-500/10",    icon: "🚨" },
      { label: "Healthy",          value: "—", color: "text-green-400",  bg: "bg-green-500/10",  icon: "✅" },
      { label: "Model Accuracy",   value: "—", color: "text-amber-400",  bg: "bg-amber-500/10",  icon: "🎯" },
      { label: "Breakdowns Saved", value: "—", color: "text-purple-400", bg: "bg-purple-500/10", icon: "💰" },
    ];
  }

  return (
    <div className="grid grid-cols-5 gap-3 mb-5">
      {items.map((item, i) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1, duration: 0.4 }}
          className="bg-gray-900 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xl">{item.icon}</span>
            <div className={`text-xs px-2 py-0.5 rounded-full font-bold ${item.bg} ${item.color}`}>
              LIVE
            </div>
          </div>
          <div className={`text-2xl font-black ${item.color}`}>
            {item.value}
          </div>
          <div className="text-xs text-white/40 mt-1">{item.label}</div>
        </motion.div>
      ))}
    </div>
  );
}

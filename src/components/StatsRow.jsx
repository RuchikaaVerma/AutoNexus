import { motion } from "framer-motion";

export default function StatsRow({ stats }) {
  const items = [
    {
      label: "Total Vehicles",
      value: stats.total,
      color: "text-cyan-400",
      bg:    "bg-cyan-500/10",
      icon:  "🚗",
    },
    {
      label: "Active Alerts",
      value: stats.alerts,
      color: "text-red-400",
      bg:    "bg-red-500/10",
      icon:  "🚨",
    },
    {
      label: "Healthy",
      value: stats.healthy,
      color: "text-green-400",
      bg:    "bg-green-500/10",
      icon:  "✅",
    },
    {
      label: "Model Accuracy",
      value: stats.accuracy + "%",
      color: "text-amber-400",
      bg:    "bg-amber-500/10",
      icon:  "🎯",
    },
    {
      label: "Breakdowns Saved",
      value: "₹" + stats.moneySaved / 1000 + "K",
      color: "text-purple-400",
      bg:    "bg-purple-500/10",
      icon:  "💰",
    },
  ];

  return (
    <div className="grid grid-cols-5 gap-3 mb-5">
      {items.map((item, i) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1, duration: 0.4 }}
          className="bg-gray-900 border border-white/5
                     rounded-xl p-4 hover:border-white/10
                     transition-all"
        >
          {/* Icon + Live badge */}
          <div className="flex items-center justify-between mb-2">
            <span className="text-xl">{item.icon}</span>
            <div className={`text-xs px-2 py-0.5 rounded-full
                            font-bold ${item.bg} ${item.color}`}>
              LIVE
            </div>
          </div>

          {/* Value */}
          <div className={`text-2xl font-black ${item.color}`}>
            {item.value}
          </div>

          {/* Label */}
          <div className="text-xs text-white/40 mt-1">
            {item.label}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
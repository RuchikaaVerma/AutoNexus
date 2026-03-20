import { statusColor } from "../utils/helpers";

export default function VehicleCard({ vehicle, selected, onClick }) {
  const emoji = {
    critical: "🔴",
    warning:  "⚠️",
    healthy:  "✅"
  }[vehicle.status];

  const color = statusColor(vehicle.status);

  return (
    <div
      onClick={onClick}
      className={`rounded-xl p-4 border cursor-pointer
                  transition-all duration-200
                  hover:-translate-y-0.5 ${
        selected
          ? "bg-gray-700 border-cyan-500/50 shadow-lg"
          : "bg-gray-800 border-white/5 hover:border-cyan-500/30"
      }`}
      style={selected
        ? { boxShadow: "0 0 20px rgba(0,200,255,0.1)" }
        : {}
      }
    >
      {/* Selected indicator */}
      {selected && (
        <div className="text-xs text-cyan-400 font-bold
                        tracking-widest mb-2">
          ● SELECTED
        </div>
      )}

      {/* Color strip */}
      <div
        className="h-0.5 rounded-full mb-3"
        style={{ background: color }}
      />

      {/* ID + Emoji */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs text-white/30 font-mono">
          {vehicle.id}
        </span>
        <span className="text-base">{emoji}</span>
      </div>

      {/* Name */}
      <div className="font-semibold text-sm text-white mb-1">
        {vehicle.name}
      </div>

      {/* Owner */}
      <div className="text-xs text-white/40 mb-3">
        👤 {vehicle.owner}
      </div>

      {/* Brake temp */}
      <div className="bg-gray-900 rounded-lg p-2.5 mb-3">
        <div className="text-xs text-white/30 mb-0.5">Brake Temp</div>
        <div
          className="text-xl font-black"
          style={{ color }}
        >
          {vehicle.sensors.brakeTemp}°C
        </div>
      </div>

      {/* Oil + Engine */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-gray-900 rounded-lg p-2">
          <div className="text-xs text-white/30">Oil</div>
          <div className="text-sm font-bold text-white">
            {vehicle.sensors.oilPressure} PSI
          </div>
        </div>
        <div className="bg-gray-900 rounded-lg p-2">
          <div className="text-xs text-white/30">Engine</div>
          <div className="text-sm font-bold text-white">
            {vehicle.sensors.engineTemp}°C
          </div>
        </div>
      </div>

      {/* Status badge */}
      <span
        className="text-xs font-bold px-2.5 py-1 rounded-full uppercase"
        style={{ background: color + "20", color }}
      >
        {vehicle.status}
      </span>
    </div>
  );
}

import { useState } from "react";
import VehicleCard  from "./VehicleCard";

const filters = ["all", "critical", "warning", "healthy"];

const filterColor = {
  all:      "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
  critical: "text-red-400 border-red-500/30 bg-red-500/10",
  warning:  "text-amber-400 border-amber-500/30 bg-amber-500/10",
  healthy:  "text-green-400 border-green-500/30 bg-green-500/10",
};

export default function VehicleGrid({ vehicles, selectedId, onSelect }) {
  const [filter, setFilter] = useState("all");

  const shown = filter === "all"
    ? vehicles
    : vehicles.filter(v => v.status === filter);

  const counts = {
    all:      vehicles.length,
    critical: vehicles.filter(v => v.status === "critical").length,
    warning:  vehicles.filter(v => v.status === "warning").length,
    healthy:  vehicles.filter(v => v.status === "healthy").length,
  };

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">
          Vehicle Health Map
        </h2>
        <span className="text-xs text-white/30">
          {shown.length} vehicles
        </span>
      </div>

      {/* Filter buttons */}
      <div className="flex gap-2 mb-4">
        {filters.map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`text-xs px-3 py-1.5 rounded-lg font-semibold
                        border transition-all ${
              filter === f
                ? filterColor[f]
                : "text-white/30 border-transparent hover:text-white/60"
            }`}
          >
            {f.toUpperCase()}
            <span className="ml-1.5 opacity-60">{counts[f]}</span>
          </button>
        ))}
      </div>

      {/* Cards — onSelect pass karo */}
      <div className="grid grid-cols-2 gap-3">
        {shown.map(v => (
          <VehicleCard
            key={v.id}
            vehicle={v}
            selected={v.id === selectedId}
            onClick={() => onSelect(v)}
          />
        ))}
      </div>

      {shown.length === 0 && (
        <div className="text-center py-10 text-white/30 text-sm">
          Is category mein koi vehicle nahi
        </div>
      )}

    </div>
  );
}
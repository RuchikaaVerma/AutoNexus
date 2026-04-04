import { urgencyColor } from "../utils/helpers";

export default function PredictionList({ predictions }) {
  // ── Safety check — never crash if undefined/empty ──────────
  if (!predictions || !Array.isArray(predictions) || predictions.length === 0) {
    return (
      <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="font-bold text-sm text-white">Failure Predictions</h2>
          <span className="text-xs bg-green-500/10 text-green-400 border border-green-500/20 px-2 py-0.5 rounded-full">
            All clear
          </span>
        </div>
        <div className="text-center py-6 text-white/25 text-xs">
          ✅ No critical predictions<br />All vehicles healthy
        </div>
      </div>
    );
  }

  const criticalCount = predictions.filter(
    p => (p.priority === "CRITICAL" || p.status === "critical")
  ).length;

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">Failure Predictions</h2>
        <span className="text-xs bg-red-500/10 text-red-400 border border-red-500/20 px-2 py-0.5 rounded-full">
          {criticalCount} critical
        </span>
      </div>

      {/* Predictions list */}
      <div className="flex flex-col gap-3">
        {predictions.map((p, idx) => {
          // ── Support BOTH old mockData shape AND new backend shape ──
          const vehicleId       = p.vehicleId  || p.id       || "VEH???";
          const component       = p.component  || p.vehicle  || "Unknown";
          const daysUntilFail   = p.daysUntilFailure ?? p.days ?? 30;
          const probability     = p.probability ?? 50;
          const factors         = Array.isArray(p.factors) ? p.factors : [];
          const color           = urgencyColor(daysUntilFail);

          return (
            <div
              key={vehicleId + idx}
              className="bg-gray-800 rounded-xl p-3 border-l-2 hover:bg-gray-750 transition-all hover:translate-x-0.5"
              style={{ borderLeftColor: color }}
            >
              {/* Top row */}
              <div className="flex justify-between items-start mb-1">
                <div>
                  <div className="text-sm font-semibold text-white">{vehicleId}</div>
                  <div className="text-xs text-white/40 mt-0.5">{component}</div>
                </div>
                <span
                  className="text-xs font-black px-2 py-0.5 rounded-full"
                  style={{ background: color + "20", color }}
                >
                  {daysUntilFail}d
                </span>
              </div>

              {/* Probability bar */}
              <div className="mt-2">
                <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: probability + "%", background: color }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-white/30">Probability</span>
                  <span className="text-xs font-bold" style={{ color }}>
                    {probability}%
                  </span>
                </div>
              </div>

              {/* Factors — only if present */}
              {factors.length > 0 && (
                <div className="mt-2 flex flex-col gap-0.5">
                  {factors.map((f, i) => (
                    <div key={i} className="text-xs text-white/30">· {f}</div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
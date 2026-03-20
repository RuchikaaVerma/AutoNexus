import { urgencyColor } from "../utils/helpers";

export default function PredictionList({ predictions }) {
  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">

      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">
          Failure Predictions
        </h2>
        <span className="text-xs bg-red-500/10 text-red-400
                         border border-red-500/20 px-2 py-0.5 rounded-full">
          {predictions.filter(p => p.priority === "CRITICAL").length} critical
        </span>
      </div>

      {/* Predictions list */}
      <div className="flex flex-col gap-3">
        {predictions.map(p => {
          const color = urgencyColor(p.daysUntilFailure);

          return (
            <div
              key={p.vehicleId}
              className="bg-gray-800 rounded-xl p-3
                         border-l-2 hover:bg-gray-750
                         transition-all hover:translate-x-0.5"
              style={{ borderLeftColor: color }}
            >

              {/* Top row — Vehicle ID + Days badge */}
              <div className="flex justify-between items-start mb-1">
                <div>
                  <div className="text-sm font-semibold text-white">
                    {p.vehicleId}
                  </div>
                  <div className="text-xs text-white/40 mt-0.5">
                    {p.component}
                  </div>
                </div>
                <span
                  className="text-xs font-black px-2 py-0.5 rounded-full"
                  style={{
                    background: color + "20",
                    color: color
                  }}
                >
                  {p.daysUntilFailure}d
                </span>
              </div>

              {/* Probability bar */}
              <div className="mt-2">
                <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: p.probability + "%",
                      background: color
                    }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-xs text-white/30">
                    Probability
                  </span>
                  <span
                    className="text-xs font-bold"
                    style={{ color }}
                  >
                    {p.probability}%
                  </span>
                </div>
              </div>

              {/* Factors */}
              <div className="mt-2 flex flex-col gap-0.5">
                {p.factors.map((f, i) => (
                  <div key={i} className="text-xs text-white/30">
                    · {f}
                  </div>
                ))}
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}

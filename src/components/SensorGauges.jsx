import { motion } from "framer-motion";

export default function SensorGauges({ vehicle }) {
  if (!vehicle) return null;

  const s = vehicle.sensors;

  const gauges = [
    {
      name:   "Brake Temperature",
      value:  s.brakeTemp,
      max:    120,
      unit:   "°C",
      danger: s.brakeTemp > 75,
    },
    {
      name:   "Engine Temperature",
      value:  s.engineTemp,
      max:    120,
      unit:   "°C",
      danger: s.engineTemp > 95,
    },
    {
      name:   "Oil Pressure",
      value:  s.oilPressure,
      max:    80,
      unit:   " PSI",
      danger: s.oilPressure < 30,
    },
    {
      name:   "Brake Fluid",
      value:  s.brakeFluid,
      max:    100,
      unit:   "%",
      danger: s.brakeFluid < 50,
    },
  ];

  return (
    <motion.div
      key={vehicle.id}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-gray-900 border border-white/5 rounded-xl p-4"
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold text-sm text-white">Live Sensors</h2>
        <span className="text-xs bg-cyan-500/10 text-cyan-400
                         border border-cyan-500/20
                         px-2 py-0.5 rounded-full">
          {vehicle.id}
        </span>
      </div>

      {/* Vehicle name */}
      <div className="text-xs text-white/40 mb-4 pb-3
                      border-b border-white/5">
        {vehicle.name} · {vehicle.owner}
      </div>

      {/* Gauges */}
      <div className="flex flex-col gap-4">
        {gauges.map((g, i) => {
          const pct   = Math.round((g.value / g.max) * 100);
          const color = g.danger ? "#ff4560" : "#00e396";

          return (
            <div key={g.name}>
              <div className="flex justify-between items-baseline mb-1.5">
                <span className="text-xs text-white/50">{g.name}</span>
                <span
                  className="text-sm font-black"
                  style={{ color }}
                >
                  {g.value}{g.unit}
                </span>
              </div>

              {/* Track */}
              <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                {/* Animated fill */}
                <motion.div
                  className="h-full rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: pct + "%" }}
                  transition={{ duration: 0.8, delay: i * 0.1 }}
                  style={{ background: color }}
                />
              </div>

              {g.danger && (
                <div className="text-xs text-red-400 mt-1">
                  ⚠️ Abnormal reading
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Mileage */}
      <div className="mt-4 pt-3 border-t border-white/5
                      flex justify-between">
        <span className="text-xs text-white/40">Mileage</span>
        <span className="text-sm font-bold text-white">
          {vehicle.mileage.toLocaleString()} km
        </span>
      </div>

    </motion.div>
  );
}
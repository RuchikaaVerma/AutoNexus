import {
  LineChart, Line,
  BarChart, Bar,
  XAxis, YAxis,
  CartesianGrid, Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts";

import { predictions, dashStats } from "../data/mockData";
import { urgencyColor }           from "../utils/helpers";

const weekData = [
  { day: "Mon",   temp: 64 },
  { day: "Tue",   temp: 68 },
  { day: "Wed",   temp: 72 },
  { day: "Thu",   temp: 77 },
  { day: "Fri",   temp: 80 },
  { day: "Sat",   temp: 84 },
  { day: "Today", temp: 88 },
];

const fleetHealth = [
  { name: "Healthy",  value: 6, color: "#00e396" },
  { name: "Warning",  value: 2, color: "#ffaa00" },
  { name: "Critical", value: 2, color: "#ff4560" },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-800 border border-white/10 rounded-lg px-3 py-2 text-xs">
        <div className="text-white/50 mb-1">{label}</div>
        <div className="font-bold text-cyan-400">{payload[0].value}°C</div>
      </div>
    );
  }
  return null;
};

export default function Analytics() {
  return (
    <div className="pt-16 min-h-screen bg-gray-950 p-5">

      {/* PAGE TITLE */}
      <div className="mb-6">
        <p className="text-xs text-white/30 tracking-widest uppercase mb-1">
          Intelligence
        </p>
        <h1 className="text-2xl font-bold text-white">
          Analytics & Predictions
        </h1>
      </div>

      {/* METRIC CARDS */}
      <div className="grid grid-cols-3 gap-4 mb-6">

        <div className="bg-gray-900 border border-white/5 rounded-xl p-5">
          <div className="text-3xl font-black text-cyan-400">{dashStats.accuracy}%</div>
          <div className="text-sm text-white/50 mt-1">Model Accuracy</div>
          <div className="text-xs text-green-400 mt-2">↑ 4% from last month</div>
        </div>

        <div className="bg-gray-900 border border-white/5 rounded-xl p-5">
          <div className="text-3xl font-black text-green-400">87%</div>
          <div className="text-sm text-white/50 mt-1">Customer Engagement Rate</div>
          <div className="text-xs text-green-400 mt-2">↑ 12% improvement</div>
        </div>

        <div className="bg-gray-900 border border-white/5 rounded-xl p-5">
          <div className="text-3xl font-black text-amber-400">24</div>
          <div className="text-sm text-white/50 mt-1">Predictions This Week</div>
          <div className="text-xs text-white/30 mt-2">8 critical · 6 warning · 10 routine</div>
        </div>

      </div>

      {/* CHARTS ROW */}
      <div className="grid grid-cols-2 gap-4 mb-4">

        {/* Line Chart */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-5">
          <h3 className="text-xs font-bold tracking-widest text-white/40 uppercase mb-5">
            Brake Temp Trend — Fleet Avg (Last 7 Days)
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={weekData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="day" tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={{ stroke: "rgba(255,255,255,0.1)" }} tickLine={false} />
              <YAxis domain={[55, 95]} tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={{ stroke: "rgba(255,255,255,0.1)" }} tickLine={false} tickFormatter={v => v + "°"} />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="temp"
                stroke="#00c8ff"
                strokeWidth={2}
                dot={(props) => {
                  const { cx, cy, payload } = props;
                  const color = payload.temp > 75 ? "#ff4560" : "#00c8ff";
                  return <circle key={cx} cx={cx} cy={cy} r={4} fill={color} stroke="none" />;
                }}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-3">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-cyan-400" />
              <span className="text-xs text-white/40">Normal</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <span className="text-xs text-white/40">Above 75°C</span>
            </div>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="bg-gray-900 border border-white/5 rounded-xl p-5">
          <h3 className="text-xs font-bold tracking-widest text-white/40 uppercase mb-5">
            Fleet Health Distribution
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={fleetHealth} barSize={48}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "rgba(255,255,255,0.3)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: "#1f2937", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "12px" }}
                labelStyle={{ color: "rgba(255,255,255,0.5)" }}
                itemStyle={{ color: "#fff" }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {fleetHealth.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

      </div>

      {/* PREDICTIONS TABLE */}
      <div className="bg-gray-900 border border-white/5 rounded-xl p-5">
        <h3 className="text-xs font-bold tracking-widest text-white/40 uppercase mb-4">
          All Upcoming Failures
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {predictions.map(p => {
            const color = urgencyColor(p.daysUntilFailure);
            return (
              <div key={p.vehicleId}
                className="flex items-center gap-4 p-3 bg-gray-800 rounded-xl border-l-2"
                style={{ borderLeftColor: color }}>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold text-white">{p.vehicleId}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full font-bold"
                      style={{ background: color + "20", color }}>
                      {p.priority}
                    </span>
                  </div>
                  <div className="text-xs text-white/50">{p.component}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-black" style={{ color }}>{p.daysUntilFailure}d</div>
                  <div className="text-xs text-white/30">{p.probability}% likely</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
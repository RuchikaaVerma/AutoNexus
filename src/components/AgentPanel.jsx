export default function AgentPanel({ agents, activeAgent }) {
  const master  = agents.find(a => a.id === "master");
  const workers = agents.filter(a => a.id !== "master");

  // Agent ka style decide karo
  function getStyle(agent) {
    // Demo mode mein active agent
    if (activeAgent === agent.id) {
      return {
        wrapper: "bg-amber-500/10 border border-amber-500/40",
        dot:     "#ffaa00",
        label:   "● PROCESSING",
        glow:    "0 0 20px rgba(255,170,0,0.2)",
      };
    }
    if (agent.status === "active" || agent.id === "master") {
      return {
        wrapper: "bg-cyan-500/5 border border-cyan-500/25",
        dot:     "#00c8ff",
        label:   "● ACTIVE",
        glow:    "none",
      };
    }
    return {
      wrapper: "bg-gray-800 border border-white/5",
      dot:     "#ffffff20",
      label:   "○ IDLE",
      glow:    "none",
    };
  }

  const masterStyle = getStyle(master);

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">

      <h2 className="font-bold text-sm text-white mb-4">
        AI Agent Orchestration
      </h2>

      {/* Master Agent */}
      <div
        className={`rounded-xl p-3 text-center mb-2
                    transition-all duration-500 ${masterStyle.wrapper}`}
        style={{ boxShadow: masterStyle.glow }}
      >
        <div className="text-2xl mb-1">{master.icon}</div>
        <div className="text-sm font-bold text-white">
          {master.name}
        </div>
        <div
          className="text-xs mt-1 font-bold"
          style={{ color: masterStyle.dot }}
        >
          {masterStyle.label}
        </div>
      </div>

      <div className="text-center text-white/20 text-xs mb-2">
        ↓ coordinates ↓
      </div>

      {/* Worker Agents */}
      <div className="grid grid-cols-3 gap-2">
        {workers.map(a => {
          const st = getStyle(a);
          return (
            <div
              key={a.id}
              className={`rounded-lg p-2.5 text-center
                          transition-all duration-500 ${st.wrapper}`}
              style={{ boxShadow: st.glow }}
            >
              <div className="text-xl mb-1">{a.icon}</div>
              <div className="text-xs font-medium text-white/70">
                {a.name}
              </div>
              <div
                className="text-xs mt-1 font-bold"
                style={{ color: st.dot }}
              >
                {st.label}
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}

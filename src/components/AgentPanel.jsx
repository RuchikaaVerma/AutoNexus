export default function AgentPanel({ agents, activeAgent }) {
  // ── Safety check ─────────────────────────────────────────────
  if (!agents || !Array.isArray(agents) || agents.length === 0) {
    return (
      <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
        <h2 className="font-bold text-sm text-white mb-4">AI Agent Orchestration</h2>
        <div className="text-center text-white/25 text-xs py-4">Loading agents...</div>
      </div>
    );
  }

  // ── Normalize — support both {id, name} and {name} shapes ────
  const normalized = agents.map(a => ({
    ...a,
    id:   a.id   || a.name || "unknown",
    name: a.name || a.id   || "Agent",
    icon: a.icon || "🤖",
  }));

  const master  = normalized.find(a =>
    a.id === "master" || a.name === "MasterAgent" || a.id === "MasterAgent"
  ) || {
    id: "master", name: "MasterAgent", icon: "🧠", status: "active"
  };

  const workers = normalized.filter(a =>
    a.id !== master.id && a.name !== master.name
  );

  function getStyle(agent) {
    // Match by id OR name (handles both shapes)
    const isActive = activeAgent &&
      (activeAgent === agent.id || activeAgent === agent.name);

    if (isActive) {
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
        className={`rounded-xl p-3 text-center mb-2 transition-all duration-500 ${masterStyle.wrapper}`}
        style={{ boxShadow: masterStyle.glow }}
      >
        <div className="text-2xl mb-1">{master.icon}</div>
        <div className="text-sm font-bold text-white">{master.name}</div>
        <div className="text-xs mt-1 font-bold" style={{ color: masterStyle.dot }}>
          {masterStyle.label}
        </div>
      </div>

      <div className="text-center text-white/20 text-xs mb-2">↓ coordinates ↓</div>

      {/* Worker Agents */}
      <div className="grid grid-cols-3 gap-2">
        {workers.map((a, idx) => {
          const st = getStyle(a);
          return (
            <div
              key={a.id + idx}
              className={`rounded-lg p-2.5 text-center transition-all duration-500 ${st.wrapper}`}
              style={{ boxShadow: st.glow }}
            >
              <div className="text-xl mb-1">{a.icon}</div>
              <div className="text-xs font-medium text-white/70 leading-tight">
                {a.name.replace("Agent", "").replace("Person2", "P2 ")}
              </div>
              <div className="text-xs mt-1 font-bold" style={{ color: st.dot }}>
                {st.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
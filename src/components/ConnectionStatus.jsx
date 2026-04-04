import { useState, useEffect } from "react";

export default function ConnectionStatus() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    const url = import.meta.env.VITE_API_URL || "http://localhost:8000";
    function check() {
      fetch(`${url}/health`)
        .then(r => setStatus(r.ok ? "connected" : "error"))
        .catch(() => setStatus("disconnected"));
    }
    check();
    const t = setInterval(check, 10000);
    return () => clearInterval(t);
  }, []);

  const s = {
    connected:    { color: "#00ff9d", text: "● Backend Connected" },
    disconnected: { color: "#ff2d55", text: "● Backend Offline"   },
    checking:     { color: "#ffb800", text: "● Checking..."       },
    error:        { color: "#ffb800", text: "⚠ Backend Error"     },
  }[status];

  return (
    <div style={{
      fontFamily:    "'Orbitron',monospace",
      fontSize:      ".58rem",
      letterSpacing: "1.5px",
      color:         s.color,
      padding:       "4px 12px",
      borderRadius:  "20px",
      background:    s.color + "12",
      border:        `1px solid ${s.color}30`,
    }}>
      {s.text}
    </div>
  );
}
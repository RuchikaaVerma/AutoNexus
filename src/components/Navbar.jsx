import { Link, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

const links = [
  { path: "/",          label: "Dashboard" },
  { path: "/analytics", label: "Analytics" },
  { path: "/security",  label: "Security"  },
];

export default function Navbar() {
  const loc = useLocation();

  // Live clock
  const [time, setTime] = useState("");

  useEffect(() => {
    function update() {
      setTime(new Date().toLocaleTimeString("en-IN", {
        hour12: false
      }));
    }
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 h-14
                    bg-gray-950/95 backdrop-blur
                    border-b border-white/5
                    flex items-center justify-between px-6">

      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-cyan-500
                        flex items-center justify-center text-sm">
          ⚡
        </div>
        <div>
          <div className="font-bold text-sm tracking-widest text-white">
            AutoNexus AI
          </div>
          <div className="text-xs text-white/25 tracking-widest">
            PREDICTIVE INTELLIGENCE
          </div>
        </div>
      </div>

      {/* Nav tabs */}
      <div className="flex gap-1 bg-white/5 rounded-xl p-1">
        {links.map(l => (
          <Link
            key={l.path}
            to={l.path}
            className={`px-5 py-1.5 rounded-lg text-sm font-medium
                        transition-all ${
              loc.pathname === l.path
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "text-white/40 hover:text-white/70"
            }`}
          >
            {l.label}
          </Link>
        ))}
      </div>

      {/* Right — clock + live */}
      <div className="flex items-center gap-4">
        <span className="text-xs text-white/25 font-mono">
          {time}
        </span>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-green-400 text-xs font-bold tracking-widest">
            LIVE
          </span>
        </div>
      </div>

    </nav>
  );
}

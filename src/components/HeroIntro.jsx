import { useEffect, useRef } from "react";

export default function HeroIntro({ onDone }) {
  const laptopRef = useRef(null);
  const screenRef = useRef(null);

  useEffect(() => {
    let frame;
    let start = null;
    const duration = 3000; // 3 second animation

    function animate(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);

      // Easing function — smooth deceleration
      const ease = 1 - Math.pow(1 - progress, 3);

      if (laptopRef.current) {
        // 3D rotate — UNESCO jaisa perspective
        const rotateX = 45 - ease * 45;   // 45deg se 0deg
        const rotateY = -20 + ease * 20;  // -20deg se 0deg
        const scale   = 0.7 + ease * 0.3; // 0.7 se 1.0

        laptopRef.current.style.transform =
          `perspective(1200px) 
           rotateX(${rotateX}deg) 
           rotateY(${rotateY}deg) 
           scale(${scale})`;
      }

      if (screenRef.current) {
        // Screen content scroll effect
        const scrollY = (1 - ease) * 40;
        screenRef.current.style.transform =
          `translateY(${scrollY}px)`;
        screenRef.current.style.opacity = ease;
      }

      if (progress < 1) {
        frame = requestAnimationFrame(animate);
      } else {
        // Animation complete — 1 second baad hide karo
        setTimeout(() => onDone && onDone(), 1000);
      }
    }

    frame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{
        background: "radial-gradient(ellipse at center, #0a0f1e 0%, #030408 100%)",
      }}
    >
      {/* Background grid lines */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,200,255,0.3) 1px, transparent 1px)," +
            "linear-gradient(90deg, rgba(0,200,255,0.3) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />

      {/* Ambient glow */}
      <div
        className="absolute rounded-full"
        style={{
          width: "600px", height: "400px",
          background: "radial-gradient(ellipse, rgba(0,200,255,0.08), transparent 70%)",
          top: "50%", left: "50%",
          transform: "translate(-50%, -50%)",
          filter: "blur(40px)",
        }}
      />

      {/* 3D Laptop */}
      <div
        ref={laptopRef}
        style={{
          transformStyle: "preserve-3d",
          transition: "none",
          willChange: "transform",
        }}
      >
        {/* Laptop shell */}
        <div
          style={{
            width: "580px",
            background: "linear-gradient(145deg, #1a1f2e, #0d1018)",
            borderRadius: "16px 16px 0 0",
            padding: "16px",
            border: "1px solid rgba(0,200,255,0.15)",
            boxShadow:
              "0 0 60px rgba(0,200,255,0.1), " +
              "inset 0 1px 0 rgba(255,255,255,0.05)",
            position: "relative",
          }}
        >
          {/* Camera dot */}
          <div
            style={{
              width: "6px", height: "6px",
              borderRadius: "50%",
              background: "rgba(0,200,255,0.4)",
              margin: "0 auto 10px",
            }}
          />

          {/* Screen */}
          <div
            style={{
              background: "#03040a",
              borderRadius: "8px",
              height: "320px",
              overflow: "hidden",
              border: "1px solid rgba(0,200,255,0.1)",
              position: "relative",
            }}
          >
            <div ref={screenRef} style={{ opacity: 0 }}>

              {/* Mini dashboard preview inside screen */}
              {/* Navbar */}
              <div style={{
                background: "#070912",
                borderBottom: "1px solid rgba(0,200,255,0.1)",
                padding: "8px 16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{
                    width: "18px", height: "18px",
                    background: "#00c8ff",
                    borderRadius: "4px",
                    display: "flex", alignItems: "center",
                    justifyContent: "center",
                    fontSize: "10px",
                  }}>⚡</div>
                  <span style={{
                    fontSize: "9px", fontWeight: "bold",
                    color: "white", letterSpacing: "2px",
                    fontFamily: "monospace",
                  }}>AutoNexus AI</span>
                </div>
                <div style={{ display: "flex", gap: "4px" }}>
                  {["Dashboard", "Analytics", "Security"].map(t => (
                    <span key={t} style={{
                      fontSize: "7px", color: "rgba(255,255,255,0.4)",
                      padding: "2px 6px",
                      background: t === "Dashboard"
                        ? "rgba(0,200,255,0.15)" : "transparent",
                      borderRadius: "4px",
                      color: t === "Dashboard"
                        ? "#00c8ff" : "rgba(255,255,255,0.3)",
                    }}>{t}</span>
                  ))}
                </div>
                <div style={{
                  display: "flex", alignItems: "center",
                  gap: "4px",
                }}>
                  <div style={{
                    width: "5px", height: "5px",
                    borderRadius: "50%",
                    background: "#00e396",
                  }} />
                  <span style={{
                    fontSize: "7px", color: "#00e396",
                    fontWeight: "bold", letterSpacing: "1px",
                  }}>LIVE</span>
                </div>
              </div>

              {/* Mini stats */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(5, 1fr)",
                gap: "6px", padding: "10px 12px 6px",
              }}>
                {[
                  { label: "Vehicles", val: "10", color: "#00c8ff" },
                  { label: "Alerts",   val: "3",  color: "#ff4560" },
                  { label: "Healthy",  val: "6",  color: "#00e396" },
                  { label: "Accuracy", val: "92%",color: "#ffaa00" },
                  { label: "Saved",    val: "₹45K",color: "#a855f7"},
                ].map(s => (
                  <div key={s.label} style={{
                    background: "#0c0e1a",
                    borderRadius: "6px",
                    padding: "6px",
                    border: "1px solid rgba(255,255,255,0.05)",
                  }}>
                    <div style={{
                      fontSize: "11px", fontWeight: "900",
                      color: s.color, fontFamily: "monospace",
                    }}>{s.val}</div>
                    <div style={{
                      fontSize: "6px", color: "rgba(255,255,255,0.3)",
                      marginTop: "2px",
                    }}>{s.label}</div>
                  </div>
                ))}
              </div>

              {/* Mini vehicle cards */}
              <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "5px", padding: "0 12px",
              }}>
                {[
                  { id: "VEH001", color: "#ff4560", temp: "85°C" },
                  { id: "VEH002", color: "#ffaa00", temp: "72°C" },
                  { id: "VEH003", color: "#00e396", temp: "62°C" },
                  { id: "VEH004", color: "#00e396", temp: "65°C" },
                  { id: "VEH005", color: "#00e396", temp: "60°C" },
                  { id: "VEH006", color: "#ffaa00", temp: "70°C" },
                  { id: "VEH007", color: "#00e396", temp: "63°C" },
                  { id: "VEH008", color: "#00e396", temp: "66°C" },
                ].map(v => (
                  <div key={v.id} style={{
                    background: "#0c0e1a",
                    borderRadius: "5px",
                    padding: "5px",
                    border: `1px solid ${v.color}30`,
                  }}>
                    <div style={{
                      height: "1px",
                      background: v.color,
                      borderRadius: "1px",
                      marginBottom: "4px",
                    }} />
                    <div style={{
                      fontSize: "6px",
                      color: "rgba(255,255,255,0.3)",
                    }}>{v.id}</div>
                    <div style={{
                      fontSize: "9px", fontWeight: "bold",
                      color: v.color, fontFamily: "monospace",
                    }}>{v.temp}</div>
                  </div>
                ))}
              </div>

            </div>
          </div>
        </div>

        {/* Laptop base */}
        <div style={{
          width: "580px", height: "14px",
          background: "linear-gradient(180deg, #151a28, #0d1018)",
          borderRadius: "0 0 8px 8px",
          border: "1px solid rgba(0,200,255,0.1)",
          borderTop: "none",
        }} />

        {/* Laptop bottom stand */}
        <div style={{
          width: "460px", height: "6px",
          background: "#0d1018",
          borderRadius: "0 0 20px 20px",
          margin: "0 auto",
          border: "1px solid rgba(0,200,255,0.08)",
          borderTop: "none",
        }} />
      </div>

      {/* Brand text */}
      <div style={{
        position: "absolute", bottom: "80px",
        textAlign: "center",
      }}>
        <div style={{
          fontSize: "11px", letterSpacing: "5px",
          color: "rgba(0,200,255,0.6)",
          fontFamily: "monospace", fontWeight: "bold",
          marginBottom: "8px",
        }}>
          AutoNexus AI — PREDICTIVE INTELLIGENCE
        </div>
        <div style={{
          fontSize: "10px", color: "rgba(255,255,255,0.2)",
          letterSpacing: "2px",
        }}>
          IIT HACKATHON 2026
        </div>
      </div>

      {/* Loading bar */}
      <div style={{
        position: "absolute", bottom: "50px",
        width: "200px", height: "2px",
        background: "rgba(255,255,255,0.05)",
        borderRadius: "2px", overflow: "hidden",
      }}>
        <div style={{
          height: "100%",
          background: "linear-gradient(90deg, #00c8ff, #a855f7)",
          borderRadius: "2px",
          animation: "loadBar 2.8s ease forwards",
        }} />
      </div>

      <style>{`
        @keyframes loadBar {
          from { width: 0% }
          to   { width: 100% }
        }
      `}</style>

    </div>
  );
}
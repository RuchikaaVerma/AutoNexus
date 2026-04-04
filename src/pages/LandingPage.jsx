import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate  = useNavigate();
  const canvasRef = useRef(null);

  // ── Particles ──
  useEffect(() => {
    const c   = canvasRef.current;
    const ctx = c.getContext("2d");
    let W, H, pts = [], raf;

    function resize() {
      W = c.width  = window.innerWidth;
      H = c.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    for (let i = 0; i < 90; i++) {
      pts.push({
        x:  Math.random() * window.innerWidth,
        y:  Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        r:  Math.random() * 1.2 + 0.3,
        o:  Math.random() * 0.4 + 0.1,
      });
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      pts.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0,229,255,${p.o})`;
        ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    }
    draw();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  // ── Enter Dashboard ──
  function handleEnter() {
    const landing = document.getElementById("landing-root");
    landing.style.transition = "opacity 0.8s ease, transform 0.8s ease";
    landing.style.opacity    = "0";
    landing.style.transform  = "scale(1.08) translateZ(200px)";
    setTimeout(() => navigate("/"), 800);
  }

  return (
    <div
      id="landing-root"
      style={{
        position:        "fixed",
        inset:           0,
        background:      "#020408",
        display:         "flex",
        flexDirection:   "column",
        alignItems:      "center",
        justifyContent:  "center",
        overflow:        "hidden",
        fontFamily:      "'DM Sans', sans-serif",
        perspective:     "1400px",
      }}
    >
      {/* Google Fonts */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=DM+Sans:wght@300;400;600&display=swap');

        @keyframes drift {
          0%,100% { transform: rotateY(-12deg) rotateX(4deg) translateY(0px); }
          33%      { transform: rotateY(0deg)   rotateX(2deg) translateY(-12px); }
          66%      { transform: rotateY(10deg)  rotateX(4deg) translateY(-6px); }
        }
        @keyframes scan {
          0%   { top: 5%;  opacity: 0; }
          10%  { opacity: 1; }
          90%  { opacity: 1; }
          100% { top: 95%; opacity: 0; }
        }
        @keyframes refPulse {
          0%,100% { opacity:.6; transform:translateX(-50%) scaleX(1); }
          50%     { opacity:1;  transform:translateX(-50%) scaleX(1.08); }
        }
        @keyframes pinPulse {
          0%,100% { transform: scale(1); }
          50%     { transform: scale(1.12); }
        }
        @keyframes pinOuter {
          0%,100% { transform:scale(1);   opacity:.3; }
          50%     { transform:scale(1.5); opacity:0; }
        }
        @keyframes carDrop {
          from { opacity:0; transform:translateY(-80px) rotateX(30deg) scale(0.8); }
          to   { opacity:1; transform:translateY(0)    rotateX(0deg)   scale(1);   }
        }
        @keyframes heroUp {
          from { opacity:0; transform:translateY(32px); }
          to   { opacity:1; transform:translateY(0); }
        }
        @keyframes stPop {
          from { opacity:0; transform:scale(.5); }
          to   { opacity:1; transform:scale(1); }
        }
        @keyframes ctaIn {
          from { opacity:0; transform:scale(.8); }
          to   { opacity:1; transform:scale(1); }
        }
        @keyframes ctaPulse {
          0%,100% { transform:scale(1);    opacity:.5; }
          50%     { transform:scale(1.05); opacity:0; }
        }
        @keyframes hintIn    { from{opacity:0} to{opacity:.25} }
        @keyframes hintFloat {
          0%,100% { transform:translateX(-50%) translateY(0); }
          50%     { transform:translateX(-50%) translateY(8px); }
        }

        .car-3d     { animation: drift 9s ease-in-out infinite; transform-style: preserve-3d; filter: drop-shadow(0 40px 60px rgba(0,229,255,.25)) drop-shadow(0 0 80px rgba(0,229,255,.1)); }
        .car-wrap   { animation: carDrop 1.4s cubic-bezier(.16,1,.3,1) both; position:relative; margin-bottom:28px; }
        .scan-beam  { position:absolute; left:0; right:0; height:2px; background:linear-gradient(90deg,transparent,rgba(0,229,255,.7),transparent); filter:blur(1px); pointer-events:none; z-index:20; animation:scan 3.5s linear infinite; }
        .car-refl   { position:absolute; bottom:-8px; left:50%; width:560px; height:26px; background:radial-gradient(ellipse,rgba(0,229,255,.18),transparent 70%); filter:blur(6px); animation:refPulse 3s ease-in-out infinite; }
        .pin        { position:absolute; z-index:25; }
        .pin-ring   { width:18px; height:18px; border-radius:50%; border:1.5px solid; display:flex; align-items:center; justify-content:center; animation:pinPulse 2.2s infinite; position:relative; }
        .pin-ring::after { content:''; position:absolute; inset:-5px; border-radius:50%; border:1px solid; opacity:.3; animation:pinOuter 2.2s infinite; }
        .pin-dot    { width:6px; height:6px; border-radius:50%; }
        .pin-label  { position:absolute; white-space:nowrap; font-family:'Orbitron',monospace; font-size:.54rem; letter-spacing:1.5px; padding:3px 9px; border-radius:4px; border:1px solid; top:-28px; left:50%; transform:translateX(-50%); }
        .hero-text  { animation: heroUp 1.6s cubic-bezier(.16,1,.3,1) .2s both; text-align:center; position:relative; z-index:5; }
        .st1 { animation: stPop .5s cubic-bezier(.34,1.56,.64,1) .9s  both; }
        .st2 { animation: stPop .5s cubic-bezier(.34,1.56,.64,1) 1.05s both; }
        .st3 { animation: stPop .5s cubic-bezier(.34,1.56,.64,1) 1.2s  both; }
        .cta-btn    { animation: ctaIn .6s cubic-bezier(.34,1.56,.64,1) 1.4s both; position:relative; display:inline-flex; align-items:center; gap:14px; padding:15px 44px; border-radius:60px; font-family:'Orbitron',monospace; font-size:.78rem; font-weight:700; letter-spacing:2px; cursor:pointer; border:1px solid rgba(0,229,255,.35); background:linear-gradient(135deg,rgba(0,229,255,.12),rgba(0,255,157,.08)); color:#00e5ff; transition:all .3s; overflow:hidden; }
        .cta-btn:hover { transform:translateY(-3px); box-shadow:0 20px 48px rgba(0,229,255,.2); }
        .cta-pulse  { position:absolute; inset:-5px; border-radius:60px; border:1px solid rgba(0,229,255,.15); animation:ctaPulse 2s infinite; }
        .arr        { transition:transform .3s; }
        .cta-btn:hover .arr { transform:translateX(5px); }
        .hint       { position:absolute; bottom:28px; left:50%; display:flex; flex-direction:column; align-items:center; gap:8px; animation:hintIn 1s 2.2s ease both, hintFloat 2.5s ease-in-out infinite; opacity:.25; }
      `}</style>

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        style={{ position: "absolute", inset: 0, zIndex: 0, pointerEvents: "none" }}
      />

      {/* Grid floor */}
      <div style={{
        position:        "absolute",
        bottom:          0, left: 0, right: 0,
        height:          "42%",
        backgroundImage: "repeating-linear-gradient(90deg,transparent,transparent 59px,rgba(0,229,255,0.055) 60px), repeating-linear-gradient(0deg,transparent,transparent 59px,rgba(0,229,255,0.055) 60px)",
        transform:       "rotateX(55deg)",
        transformOrigin: "bottom center",
        maskImage:       "linear-gradient(transparent 0%,black 30%,black 70%,transparent 100%)",
        zIndex:          1,
      }} />

      {/* Ambient glow */}
      <div style={{
        position:   "absolute", inset: 0,
        background: "radial-gradient(ellipse 80% 50% at 50% -10%,rgba(0,229,255,0.04),transparent), radial-gradient(ellipse 60% 40% at 80% 80%,rgba(157,78,221,0.04),transparent)",
        pointerEvents: "none", zIndex: 1,
      }} />

      {/* ── 3D CAR ── */}
      <div className="car-wrap" style={{ zIndex: 5 }}>
        <div className="car-3d">
          <div style={{ position: "relative" }}>

            {/* Scan beam */}
            <div className="scan-beam" />

            {/* Hotspot — Brakes */}
            <div className="pin" style={{ top: 72, left: 52 }}>
              <div className="pin-ring" style={{ borderColor:"#ff2d55", color:"#ff2d55" }}>
                <div className="pin-dot" style={{ background:"#ff2d55" }} />
              </div>
              <div className="pin-label" style={{ borderColor:"rgba(255,45,85,.35)", background:"rgba(255,45,85,.08)", color:"#ff2d55" }}>
                BRAKE · 85°C
              </div>
            </div>

            {/* Hotspot — Engine */}
            <div className="pin" style={{ top: 52, right: 88 }}>
              <div className="pin-ring" style={{ borderColor:"#00ff9d", color:"#00ff9d" }}>
                <div className="pin-dot" style={{ background:"#00ff9d" }} />
              </div>
              <div className="pin-label" style={{ borderColor:"rgba(0,255,157,.35)", background:"rgba(0,255,157,.07)", color:"#00ff9d" }}>
                ENGINE · 92°C
              </div>
            </div>

            {/* Hotspot — Oil */}
            <div className="pin" style={{ top: 138, right: 36 }}>
              <div className="pin-ring" style={{ borderColor:"#ffb800", color:"#ffb800" }}>
                <div className="pin-dot" style={{ background:"#ffb800" }} />
              </div>
              <div className="pin-label" style={{ borderColor:"rgba(255,184,0,.35)", background:"rgba(255,184,0,.07)", color:"#ffb800" }}>
                OIL · 38 PSI
              </div>
            </div>

            {/* ── SVG CAR ── */}
            <svg width="600" height="230" viewBox="0 0 600 230" fill="none" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="300" cy="222" rx="280" ry="7" fill="url(#sg)" opacity="0.55"/>
              <path d="M60 162 L60 122 Q63 104 84 95 L172 63 Q208 50 242 47 L360 46 Q404 46 440 57 L512 95 Q530 104 532 122 L542 162 Z" fill="url(#bg)" stroke="rgba(0,229,255,0.42)" strokeWidth="1.5"/>
              <path d="M180 95 Q197 55 220 47 L378 45 Q404 45 420 56 L440 95 Z" fill="url(#rg)" stroke="rgba(0,229,255,0.28)" strokeWidth="1"/>
              <path d="M398 95 L378 45 L420 56 Z" fill="url(#wg)" stroke="rgba(0,229,255,.5)" strokeWidth="1" opacity=".9"/>
              <path d="M182 95 L220 47 L180 95 Z" fill="url(#wg)" stroke="rgba(0,229,255,.5)" strokeWidth="1" opacity=".9"/>
              <path d="M193 95 L212 52 L280 50 L286 95 Z" fill="url(#wg)" stroke="rgba(0,229,255,.22)" strokeWidth=".8" opacity=".88"/>
              <path d="M293 95 L293 50 L368 49 L387 95 Z" fill="url(#wg)" stroke="rgba(0,229,255,.22)" strokeWidth=".8" opacity=".88"/>
              <line x1="289" y1="95" x2="290" y2="50" stroke="rgba(0,229,255,.32)" strokeWidth="2"/>
              <line x1="280" y1="95" x2="282" y2="162" stroke="rgba(0,229,255,.1)" strokeWidth="1"/>
              <line x1="378" y1="95" x2="378" y2="162" stroke="rgba(0,229,255,.1)" strokeWidth="1"/>
              <path d="M77 126 L525 126" stroke="rgba(0,229,255,.12)" strokeWidth="1" strokeDasharray="3 6"/>
              <path d="M514 98 Q535 93 540 107 L542 122 Q536 130 517 128 Z" fill="url(#hlg)" opacity=".92"/>
              <ellipse cx="528" cy="114" rx="9" ry="7" fill="rgba(255,235,100,.95)" filter="url(#hf)"/>
              <line x1="516" y1="100" x2="534" y2="98" stroke="rgba(255,235,100,.45)" strokeWidth="2" strokeLinecap="round"/>
              <path d="M68 98 Q48 93 43 107 L41 122 Q46 130 64 128 Z" fill="url(#tlg)" opacity=".92"/>
              <ellipse cx="50" cy="114" rx="8" ry="6" fill="rgba(255,45,85,.97)" filter="url(#tf)"/>
              <path d="M518 132 Q548 135 550 155 L550 163 Q534 167 518 165 Z" fill="url(#bpg)" stroke="rgba(0,229,255,.15)" strokeWidth="1"/>
              <path d="M70 132 Q42 135 40 155 L40 163 Q56 167 70 165 Z" fill="url(#bpg)" stroke="rgba(0,229,255,.15)" strokeWidth="1"/>
              <rect x="524" y="134" width="20" height="16" rx="2" fill="none" stroke="rgba(0,229,255,.48)" strokeWidth="1"/>
              <line x1="534" y1="134" x2="534" y2="150" stroke="rgba(0,229,255,.28)" strokeWidth=".8"/>
              <line x1="524" y1="142" x2="544" y2="142" stroke="rgba(0,229,255,.28)" strokeWidth=".8"/>
              <circle cx="134" cy="174" r="40" fill="url(#tw)" stroke="rgba(0,229,255,.28)" strokeWidth="1.5"/>
              <circle cx="134" cy="174" r="25" fill="url(#rw)" stroke="rgba(0,229,255,.42)" strokeWidth="1.2"/>
              <circle cx="134" cy="174" r="7" fill="rgba(0,229,255,.65)"/>
              <g stroke="rgba(0,229,255,.48)" strokeWidth="1.8" strokeLinecap="round">
                <line x1="134" y1="149" x2="134" y2="167"/><line x1="134" y1="181" x2="134" y2="199"/>
                <line x1="109" y1="174" x2="127" y2="174"/><line x1="141" y1="174" x2="159" y2="174"/>
                <line x1="116" y1="156" x2="127" y2="167"/><line x1="141" y1="181" x2="152" y2="192"/>
                <line x1="152" y1="156" x2="141" y2="167"/><line x1="127" y1="181" x2="116" y2="192"/>
              </g>
              <circle cx="460" cy="174" r="40" fill="url(#tw)" stroke="rgba(0,229,255,.28)" strokeWidth="1.5"/>
              <circle cx="460" cy="174" r="25" fill="url(#rw)" stroke="rgba(0,229,255,.42)" strokeWidth="1.2"/>
              <circle cx="460" cy="174" r="7" fill="rgba(0,229,255,.65)"/>
              <g stroke="rgba(0,229,255,.48)" strokeWidth="1.8" strokeLinecap="round">
                <line x1="460" y1="149" x2="460" y2="167"/><line x1="460" y1="181" x2="460" y2="199"/>
                <line x1="435" y1="174" x2="453" y2="174"/><line x1="467" y1="174" x2="485" y2="174"/>
                <line x1="442" y1="156" x2="453" y2="167"/><line x1="467" y1="181" x2="478" y2="192"/>
                <line x1="478" y1="156" x2="467" y2="167"/><line x1="453" y1="181" x2="442" y2="192"/>
              </g>
              <path d="M94 152 Q96 132 134 132 Q172 132 174 152" fill="#020408" stroke="rgba(0,229,255,.16)" strokeWidth="1"/>
              <path d="M420 152 Q422 132 460 132 Q498 132 500 152" fill="#020408" stroke="rgba(0,229,255,.16)" strokeWidth="1"/>
              <path d="M432 93 L450 89 L450 97 L432 97 Z" fill="url(#bg)" stroke="rgba(0,229,255,.28)" strokeWidth="1"/>
              <circle cx="300" cy="152" r="9" fill="none" stroke="rgba(0,229,255,.42)" strokeWidth="1.5"/>
              <text x="300" y="156" textAnchor="middle" fontFamily="serif" fontSize="9" fill="rgba(0,229,255,.88)" fontWeight="bold">H</text>
              <line x1="340" y1="45" x2="340" y2="29" stroke="rgba(0,229,255,.38)" strokeWidth="1.5"/>
              <circle cx="340" cy="28" r="2.5" fill="#00e5ff" opacity=".75"/>
              <path d="M192 70 Q300 57 408 70" stroke="rgba(255,255,255,.06)" strokeWidth="9" fill="none" strokeLinecap="round"/>
              <defs>
                <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#1a2d50"/><stop offset="100%" stopColor="#080e1e"/></linearGradient>
                <linearGradient id="rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#1e3462"/><stop offset="100%" stopColor="#0d1c38"/></linearGradient>
                <linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="rgba(0,229,255,.42)"/><stop offset="100%" stopColor="rgba(0,80,190,.18)"/></linearGradient>
                <linearGradient id="tw" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stopColor="#0e1422"/><stop offset="100%" stopColor="#060910"/></linearGradient>
                <linearGradient id="rw" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stopColor="#1a2848"/><stop offset="100%" stopColor="#0b1228"/></linearGradient>
                <linearGradient id="bpg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#0d1622"/><stop offset="100%" stopColor="#080c18"/></linearGradient>
                <linearGradient id="hlg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="rgba(255,235,100,.04)"/><stop offset="100%" stopColor="rgba(255,235,100,.72)"/></linearGradient>
                <linearGradient id="tlg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="rgba(255,45,85,.72)"/><stop offset="100%" stopColor="rgba(255,45,85,.04)"/></linearGradient>
                <radialGradient id="sg"><stop offset="0%" stopColor="rgba(0,229,255,.32)"/><stop offset="100%" stopColor="transparent"/></radialGradient>
                <filter id="hf"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                <filter id="tf"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
              </defs>
            </svg>

          </div>
        </div>
        <div className="car-refl" style={{ transform: "translateX(-50%)" }} />
      </div>

      {/* ── HERO TEXT ── */}
      <div className="hero-text">
        <div style={{ fontFamily:"'Orbitron',monospace", fontSize:".6rem", letterSpacing:"5px", color:"rgba(0,229,255,.6)", marginBottom:"12px" }}>
          IITM HACKATHON 2026 &nbsp;·&nbsp; AUTONOMOUS SYSTEMS
        </div>

        <div style={{
          fontFamily:  "'Orbitron',monospace",
          fontSize:    "clamp(2.2rem,5vw,3.8rem)",
          fontWeight:  900,
          lineHeight:  1.05,
          background:  "linear-gradient(135deg,#fff 0%,#00e5ff 45%,#00ff9d 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor:  "transparent",
          backgroundClip:       "text",
          marginBottom: "10px",
        }}>
          AutoNexus AI
        </div>

        <div style={{ fontSize:".95rem", color:"rgba(255,255,255,.3)", fontWeight:300, letterSpacing:"3px", marginBottom:"36px" }}>
          Predictive Maintenance Intelligence
        </div>

        {/* Stats */}
        <div style={{ display:"flex", gap:"40px", justifyContent:"center", marginBottom:"40px" }}>
          <div className="st1" style={{ textAlign:"center" }}>
            <div style={{ fontFamily:"'Orbitron',monospace", fontSize:"1.8rem", fontWeight:900, color:"#00e5ff" }}>10</div>
            <div style={{ fontSize:".6rem", color:"rgba(255,255,255,.3)", letterSpacing:"2.5px", marginTop:"4px" }}>VEHICLES</div>
          </div>
          <div className="st2" style={{ textAlign:"center" }}>
            <div style={{ fontFamily:"'Orbitron',monospace", fontSize:"1.8rem", fontWeight:900, color:"#00ff9d" }}>92%</div>
            <div style={{ fontSize:".6rem", color:"rgba(255,255,255,.3)", letterSpacing:"2.5px", marginTop:"4px" }}>ACCURACY</div>
          </div>
          <div className="st3" style={{ textAlign:"center" }}>
            <div style={{ fontFamily:"'Orbitron',monospace", fontSize:"1.8rem", fontWeight:900, color:"#9d4edd" }}>7</div>
            <div style={{ fontSize:".6rem", color:"rgba(255,255,255,.3)", letterSpacing:"2.5px", marginTop:"4px" }}>AI AGENTS</div>
          </div>
        </div>

        {/* CTA Button */}
        <button className="cta-btn" onClick={handleEnter}>
          <div className="cta-pulse" />
          ENTER DASHBOARD
          <span className="arr">→</span>
        </button>
      </div>

      {/* Scroll hint */}
      <div className="hint">
        <div style={{ width:"1px", height:"42px", background:"linear-gradient(transparent,#00e5ff)" }} />
        <div style={{ fontFamily:"'Orbitron',monospace", fontSize:".52rem", letterSpacing:"3px", color:"#00e5ff" }}>
          ENTER
        </div>
      </div>

    </div>
  );
}
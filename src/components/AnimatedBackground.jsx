import { useEffect, useRef } from "react";

export default function AnimatedBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf, time = 0;
    let mouse = { x: -999, y: -999, clicking: false };

    // ── Resize ──
    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      initAll();
    }

    // ── Mouse ──
    function onMove(e) { mouse.x = e.clientX; mouse.y = e.clientY; }
    function onDown()  { mouse.clicking = true;  spawnExplosion(mouse.x, mouse.y); }
    function onUp()    { mouse.clicking = false; }
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup",   onUp);
    window.addEventListener("resize",    resize);

    // ════════════════════════════
    // DATA STORES
    // ════════════════════════════
    let particles  = [];
    let roadCars   = [];
    let radarDots  = [];
    let neurons    = [];
    let explosions = [];
    let waveOffset = 0;
    let radarAngle = 0;

    function initAll() {
      const W = canvas.width, H = canvas.height;
      if (!W || !H) return;
      initParticles(W, H);
      initRoadCars(W, H);
      initNeurons(W, H);
      initRadarDots();
    }

    // ════════════════════════════
    // 1. PARTICLES — sensor data
    // ════════════════════════════
    const PCOLORS = ["0,229,255","0,255,157","255,184,0","255,45,85","157,78,221"];

    function initParticles(W, H) {
      particles = [];
      for (let i = 0; i < 90; i++) {
        particles.push({
          x:     Math.random() * W,
          y:     Math.random() * H,
          vx:    (Math.random() - 0.5) * 0.5,
          vy:    (Math.random() - 0.5) * 0.5,
          r:     Math.random() * 1.8 + 0.5,
          o:     Math.random() * 0.45 + 0.18,
          color: PCOLORS[Math.floor(Math.random() * PCOLORS.length)],
          pulse: Math.random() * Math.PI * 2,
        });
      }
    }

    function drawParticles() {
      const W = canvas.width, H = canvas.height;
      particles.forEach(p => {
        // Mouse attract
        const dx = mouse.x - p.x, dy = mouse.y - p.y;
        const d  = Math.sqrt(dx*dx + dy*dy);
        if (d < 200 && d > 0) {
          p.vx += (dx/d) * (1 - d/200) * 0.08;
          p.vy += (dy/d) * (1 - d/200) * 0.08;
        }
        p.vx *= 0.96; p.vy *= 0.96;
        p.x  += p.vx; p.y  += p.vy;
        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
        p.pulse += 0.04;

        const o = p.o + Math.sin(p.pulse) * 0.1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color},${o})`;
        ctx.fill();
      });

      // Connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i+1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d  = Math.sqrt(dx*dx + dy*dy);
          if (d < 100) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(0,229,255,${(1-d/100)*0.1})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }
    }

    // ════════════════════════════
    // 2. ROAD CARS — vehicles moving on roads
    // ════════════════════════════
    function initRoadCars(W, H) {
      roadCars = [];
      // Horizontal roads
      const roads = [H*0.2, H*0.45, H*0.7, H*0.88];
      roads.forEach((y, ri) => {
        const count = Math.floor(Math.random() * 3) + 2;
        for (let i = 0; i < count; i++) {
          const dir = ri % 2 === 0 ? 1 : -1;
          roadCars.push({
            x:     Math.random() * W,
            y:     y,
            speed: (Math.random() * 1.5 + 0.8) * dir,
            color: PCOLORS[Math.floor(Math.random() * PCOLORS.length)],
            status: Math.random() > 0.7
              ? (Math.random() > 0.5 ? "critical" : "warning")
              : "healthy",
            len:  Math.random() * 16 + 10,
            w:    5,
            trail: [],
          });
        }
      });
    }

    function drawRoadCars() {
      const W = canvas.width, H = canvas.height;

      // Draw road lines first
      const roads = [H*0.2, H*0.45, H*0.7, H*0.88];
      roads.forEach(y => {
        ctx.strokeStyle = "rgba(0,229,255,0.04)";
        ctx.lineWidth   = 1;
        ctx.setLineDash([20, 30]);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(W, y);
        ctx.stroke();
        ctx.setLineDash([]);
      });

      roadCars.forEach(car => {
        car.x += car.speed;
        if (car.x > W + 50)  car.x = -50;
        if (car.x < -50)     car.x = W + 50;

        // Trail
        car.trail.push({ x: car.x, y: car.y });
        if (car.trail.length > 18) car.trail.shift();

        // Draw trail
        car.trail.forEach((t, i) => {
          const alpha = (i / car.trail.length) * 0.12;
          ctx.beginPath();
          ctx.arc(t.x, t.y, 1.5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${car.color},${alpha})`;
          ctx.fill();
        });

        // Status color
        const sc = car.status === "critical" ? "255,45,85"
                 : car.status === "warning"  ? "255,184,0"
                 : "0,229,255";

        // Car body
        ctx.save();
        ctx.translate(car.x, car.y);
        const dir = car.speed > 0 ? 1 : -1;

        // Body
        ctx.fillStyle = `rgba(${sc},0.55)`;
        ctx.beginPath();
        ctx.roundRect(-car.len/2 * dir, -car.w/2, car.len, car.w, 2);
        ctx.fill();

        // Headlight glow
        ctx.fillStyle = `rgba(${sc},0.9)`;
        ctx.beginPath();
        ctx.arc((car.len/2) * dir, 0, 2.5, 0, Math.PI * 2);
        ctx.fill();

        // Outer glow
        const g = ctx.createRadialGradient(
          (car.len/2)*dir, 0, 0,
          (car.len/2)*dir, 0, 12
        );
        g.addColorStop(0, `rgba(${sc},0.25)`);
        g.addColorStop(1, `rgba(${sc},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc((car.len/2)*dir, 0, 12, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
      });
    }

    // ════════════════════════════
    // 3. RADAR SWEEP — vehicle scanner
    // ════════════════════════════
    function initRadarDots() {
      radarDots = [];
      for (let i = 0; i < 8; i++) {
        radarDots.push({
          angle:  Math.random() * Math.PI * 2,
          dist:   Math.random() * 0.8 + 0.1,
          o:      0,
          color:  Math.random() > 0.7 ? "255,45,85" : "0,229,255",
          fadeAt: Math.random() * Math.PI * 2,
        });
      }
    }

    function drawRadar() {
      const W = canvas.width, H = canvas.height;
      const cx = W * 0.88, cy = H * 0.22;
      const R  = Math.min(W, H) * 0.1;

      radarAngle += 0.018;

      // Outer rings
      [1, 0.66, 0.33].forEach(scale => {
        ctx.beginPath();
        ctx.arc(cx, cy, R * scale, 0, Math.PI * 2);
        ctx.strokeStyle = "rgba(0,229,255,0.08)";
        ctx.lineWidth   = 0.8;
        ctx.stroke();
      });

      // Cross lines
      ctx.strokeStyle = "rgba(0,229,255,0.06)";
      ctx.lineWidth   = 0.5;
      ctx.beginPath(); ctx.moveTo(cx-R, cy); ctx.lineTo(cx+R, cy); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cx, cy-R); ctx.lineTo(cx, cy+R); ctx.stroke();

      // Sweep gradient
      const sweep = ctx.createConicalGradient
        ? ctx.createConicalGradient(cx, cy, radarAngle)
        : null;

      // Manual sweep arc
      ctx.save();
      ctx.translate(cx, cy);
      const sweepGrad = ctx.createRadialGradient(0,0,0,0,0,R);
      sweepGrad.addColorStop(0, "rgba(0,229,255,0.18)");
      sweepGrad.addColorStop(1, "rgba(0,229,255,0)");
      ctx.fillStyle = sweepGrad;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, R, radarAngle - 0.6, radarAngle, false);
      ctx.closePath();
      ctx.fill();

      // Sweep line
      ctx.strokeStyle = "rgba(0,229,255,0.5)";
      ctx.lineWidth   = 1;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(radarAngle)*R, Math.sin(radarAngle)*R);
      ctx.stroke();
      ctx.restore();

      // Radar dots (vehicles detected)
      radarDots.forEach(dot => {
        const angleDiff = Math.abs(
          ((dot.angle - radarAngle) % (Math.PI*2) + Math.PI*2) % (Math.PI*2)
        );
        if (angleDiff < 0.1) dot.o = 1;
        dot.o *= 0.985;

        if (dot.o > 0.05) {
          const dx = cx + Math.cos(dot.angle) * R * dot.dist;
          const dy = cy + Math.sin(dot.angle) * R * dot.dist;
          ctx.beginPath();
          ctx.arc(dx, dy, 3, 0, Math.PI*2);
          ctx.fillStyle = `rgba(${dot.color},${dot.o})`;
          ctx.fill();

          // Ping ring
          ctx.beginPath();
          ctx.arc(dx, dy, 3 + (1-dot.o)*8, 0, Math.PI*2);
          ctx.strokeStyle = `rgba(${dot.color},${dot.o*0.4})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      });

      // Center dot
      ctx.beginPath();
      ctx.arc(cx, cy, 3, 0, Math.PI*2);
      ctx.fillStyle = "rgba(0,229,255,0.8)";
      ctx.fill();

      // Label
      ctx.fillStyle = "rgba(0,229,255,0.25)";
      ctx.font = "9px 'Courier New'";
      ctx.fillText("FLEET RADAR", cx - R, cy - R - 6);
    }

    // ════════════════════════════
    // 4. NEURAL NETWORK — AI agents
    // ════════════════════════════
    function initNeurons(W, H) {
      neurons = [];
      const cx = W * 0.1, cy = H * 0.55;
      const nodeCount = 9;

      // Master node
      neurons.push({ x:cx, y:cy, r:5, color:"0,229,255", pulse:0, master:true });

      // Worker nodes
      for (let i = 0; i < nodeCount-1; i++) {
        const angle = (Math.PI*2/( nodeCount-1)) * i;
        const dist  = 55 + Math.random() * 25;
        neurons.push({
          x:     cx + Math.cos(angle)*dist,
          y:     cy + Math.sin(angle)*dist,
          r:     Math.random()*2 + 1.5,
          color: PCOLORS[Math.floor(Math.random()*PCOLORS.length)],
          pulse: Math.random()*Math.PI*2,
          master:false,
        });
      }
    }

    function drawNeurons() {
      // Connections from master
      neurons.forEach((n, i) => {
        if (i === 0) return;
        const pulse = Math.sin(time * 0.03 + i) * 0.5 + 0.5;
        ctx.beginPath();
        ctx.moveTo(neurons[0].x, neurons[0].y);
        ctx.lineTo(n.x, n.y);
        ctx.strokeStyle = `rgba(0,229,255,${pulse * 0.12})`;
        ctx.lineWidth   = 0.8;
        ctx.stroke();

        // Traveling signal dot
        const t = (time * 0.02 + i * 0.7) % 1;
        const sx = neurons[0].x + (n.x - neurons[0].x) * t;
        const sy = neurons[0].y + (n.y - neurons[0].y) * t;
        ctx.beginPath();
        ctx.arc(sx, sy, 1.5, 0, Math.PI*2);
        ctx.fillStyle = `rgba(0,229,255,${pulse * 0.6})`;
        ctx.fill();
      });

      // Draw nodes
      neurons.forEach(n => {
        n.pulse += 0.05;
        const po = 0.5 + Math.sin(n.pulse) * 0.3;

        // Glow
        const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r*4);
        g.addColorStop(0, `rgba(${n.color},${po*0.3})`);
        g.addColorStop(1, `rgba(${n.color},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r*4, 0, Math.PI*2);
        ctx.fill();

        // Core
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI*2);
        ctx.fillStyle = `rgba(${n.color},${po*0.8})`;
        ctx.fill();
      });

      // Label
      ctx.fillStyle = "rgba(0,229,255,0.2)";
      ctx.font = "9px 'Courier New'";
      ctx.fillText("AI AGENTS", neurons[0].x - 20, neurons[0].y - 65);
    }

    // ════════════════════════════
    // 5. EKG HEARTBEAT — vehicle health
    // ════════════════════════════
    function drawEKG() {
      const W = canvas.width, H = canvas.height;
      waveOffset += 1.5;
      const y0    = H * 0.95;
      const steps = 220;

      ctx.beginPath();
      for (let i = 0; i < steps; i++) {
        const x   = (W / steps) * i;
        const mod = Math.floor(i + waveOffset * 0.5) % 55;
        let y     = y0;
        if      (mod === 8)  y = y0 - 8;
        else if (mod === 9)  y = y0 - 30;
        else if (mod === 10) y = y0 + 15;
        else if (mod === 11) y = y0 - 55;
        else if (mod === 12) y = y0 - 48;
        else if (mod === 13) y = y0 + 10;
        else if (mod === 14) y = y0 - 5;
        else                 y = y0 + Math.sin((x / W) * Math.PI * 2) * 3;

        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }

      const lineGrad = ctx.createLinearGradient(0, 0, W, 0);
      lineGrad.addColorStop(0,    "rgba(0,229,255,0)");
      lineGrad.addColorStop(0.3,  "rgba(0,255,157,0.15)");
      lineGrad.addColorStop(0.7,  "rgba(0,229,255,0.2)");
      lineGrad.addColorStop(1,    "rgba(0,229,255,0)");
      ctx.strokeStyle = lineGrad;
      ctx.lineWidth   = 1.5;
      ctx.stroke();
    }

    // ════════════════════════════
    // 6. GAUGE RINGS — dashboard meters
    // ════════════════════════════
    function drawGauges() {
      const W = canvas.width, H = canvas.height;

      const gauges = [
        { cx:W*0.5, cy:H*0.08, R:35, val:0.72, color:"0,229,255",  label:"BRAKE" },
        { cx:W*0.6, cy:H*0.06, R:28, val:0.45, color:"0,255,157",  label:"OIL"   },
        { cx:W*0.4, cy:H*0.06, R:28, val:0.88, color:"255,45,85",  label:"TEMP"  },
      ];

      gauges.forEach((g, gi) => {
        const animVal = g.val + Math.sin(time * 0.02 + gi) * 0.05;

        // Background arc
        ctx.beginPath();
        ctx.arc(g.cx, g.cy, g.R, Math.PI*0.75, Math.PI*2.25);
        ctx.strokeStyle = `rgba(${g.color},0.08)`;
        ctx.lineWidth   = 4;
        ctx.lineCap     = "round";
        ctx.stroke();

        // Value arc
        const endAngle = Math.PI*0.75 + animVal * Math.PI*1.5;
        ctx.beginPath();
        ctx.arc(g.cx, g.cy, g.R, Math.PI*0.75, endAngle);
        ctx.strokeStyle = `rgba(${g.color},0.35)`;
        ctx.lineWidth   = 4;
        ctx.lineCap     = "round";
        ctx.stroke();

        // Center value
        ctx.fillStyle = `rgba(${g.color},0.4)`;
        ctx.font      = `bold 10px 'Courier New'`;
        ctx.textAlign = "center";
        ctx.fillText(Math.round(animVal*100)+"%", g.cx, g.cy+3);

        // Label
        ctx.fillStyle = `rgba(${g.color},0.2)`;
        ctx.font      = "8px 'Courier New'";
        ctx.fillText(g.label, g.cx, g.cy + g.R + 12);
        ctx.textAlign = "left";
      });
    }

    // ════════════════════════════
    // 7. AMBIENT ORBS
    // ════════════════════════════
    function drawOrbs() {
      const W = canvas.width, H = canvas.height;
      const orbs = [
        { fx:0.15, fy:0.3,  r:240, c:"0,229,255",  o:0.055, s:0.0003 },
        { fx:0.85, fy:0.6,  r:200, c:"157,78,221", o:0.045, s:0.0005 },
        { fx:0.5,  fy:0.85, r:180, c:"0,255,157",  o:0.04,  s:0.0004 },
        { fx:0.7,  fy:0.15, r:160, c:"255,184,0",  o:0.03,  s:0.0006 },
      ];
      orbs.forEach((orb, i) => {
        const px = orb.fx*W + Math.sin(time*orb.s + i*2)*100;
        const py = orb.fy*H + Math.cos(time*orb.s + i)  *80;
        const g  = ctx.createRadialGradient(px,py,0,px,py,orb.r);
        g.addColorStop(0, `rgba(${orb.c},${orb.o})`);
        g.addColorStop(1, `rgba(${orb.c},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(px, py, orb.r, 0, Math.PI*2);
        ctx.fill();
      });
    }

    // ════════════════════════════
    // 8. CLICK EXPLOSION
    // ════════════════════════════
    function spawnExplosion(x, y) {
      for (let i = 0; i < 22; i++) {
        const angle = (Math.PI*2/22)*i;
        const speed = Math.random()*5+2;
        explosions.push({
          x, y,
          vx:    Math.cos(angle)*speed,
          vy:    Math.sin(angle)*speed,
          life:  1,
          r:     Math.random()*3+1,
          color: PCOLORS[Math.floor(Math.random()*PCOLORS.length)],
        });
      }
    }

    function drawExplosions() {
      explosions = explosions.filter(e => e.life > 0);
      explosions.forEach(e => {
        e.x += e.vx; e.y += e.vy;
        e.vx *= 0.92; e.vy *= 0.92;
        e.life -= 0.022;
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.r*e.life, 0, Math.PI*2);
        ctx.fillStyle = `rgba(${e.color},${e.life*0.85})`;
        ctx.fill();
      });
    }

    // ════════════════════════════
    // 9. CURSOR GLOW
    // ════════════════════════════
    function drawCursor() {
      if (mouse.x === -999) return;
      const r = mouse.clicking ? 70 : 45;
      const g = ctx.createRadialGradient(mouse.x,mouse.y,0,mouse.x,mouse.y,r);
      g.addColorStop(0, `rgba(0,229,255,${mouse.clicking?0.16:0.08})`);
      g.addColorStop(1, "rgba(0,229,255,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(mouse.x, mouse.y, r, 0, Math.PI*2);
      ctx.fill();
    }

    // ════════════════════════════
    // MAIN LOOP
    // ════════════════════════════
    function loop() {
      const W = canvas.width, H = canvas.height;
      if (!W || !H) { raf = requestAnimationFrame(loop); return; }

      ctx.clearRect(0, 0, W, H);
      time++;

      drawOrbs();
      drawRoadCars();
      drawGauges();
      drawRadar();
      drawNeurons();
      drawEKG();
      drawParticles();
      drawExplosions();
      drawCursor();

      raf = requestAnimationFrame(loop);
    }

    resize();
    loop();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("mouseup",   onUp);
      window.removeEventListener("resize",    resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position:      "fixed",
        inset:         0,
        zIndex:        0,
        pointerEvents: "none",
      }}
    />
  );
}
import { useEffect, useRef } from "react";

export default function AnimatedBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf, time = 0;
    let mouse = { x: -999, y: -999, clicking: false };
    let particles = [], circuits = [], streams = [], explosions = [];

    const COLORS = [
      "0,229,255",
      "0,255,157",
      "255,184,0",
      "255,45,85",
      "157,78,221",
    ];

  
    function resize() {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
      initAll();
    }

    function initAll() {
      const W = canvas.width;
      const H = canvas.height;
      if (!W || !H) return;

      // Particles
      particles = [];
      for (let i = 0; i < 75; i++) {
        particles.push({
          x:     Math.random() * W,
          y:     Math.random() * H,
          vx:    (Math.random() - 0.5) * 0.4,
          vy:    (Math.random() - 0.5) * 0.4,
          r:     Math.random() * 1.6 + 0.5,
          o:     Math.random() * 0.4 + 0.12,
          color: COLORS[Math.floor(Math.random() * COLORS.length)],
          pulse: Math.random() * Math.PI * 2,
        });
      }

      // Circuit lines
      circuits = [];
      const count = Math.floor(W / 120);
      for (let i = 0; i < count; i++) {
        circuits.push({
          x:     Math.random() * W,
          y:     Math.random() * H,
          len:   Math.random() * 120 + 60,
          dir:   Math.random() > 0.5 ? "h" : "v",
          pulse: Math.random() * Math.PI * 2,
          speed: Math.random() * 0.02 + 0.008,
          color: Math.random() > 0.7 ? "0,255,157" : "0,229,255",
        });
      }

      // Data streams
      streams = [];
      for (let i = 0; i < 8; i++) {
        streams.push({
          x:     Math.random() * W,
          y:     Math.random() * H,
          angle: Math.random() * Math.PI * 2,
          speed: Math.random() * 1.2 + 0.5,
          len:   Math.random() * 40 + 20,
          o:     Math.random() * 0.18 + 0.05,
          color: Math.random() > 0.5 ? "0,229,255" : "0,255,157",
        });
      }
    }

    // ── Mouse events ──
    function onMove(e) { mouse.x = e.clientX; mouse.y = e.clientY; }
    function onDown()  {
      mouse.clicking = true;
      spawnExplosion(mouse.x, mouse.y);
    }
    function onUp()    { mouse.clicking = false; }

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup",   onUp);
    window.addEventListener("resize",    resize);

    // ── Draw functions ──
    function drawOrbs() {
      const W = canvas.width, H = canvas.height;
      const orbs = [
        { fx:0.15, fy:0.25, r:220, color:"0,229,255",  o:0.028, s:0.0003 },
        { fx:0.85, fy:0.65, r:190, color:"157,78,221", o:0.022, s:0.0005 },
        { fx:0.50, fy:0.90, r:170, color:"0,255,157",  o:0.020, s:0.0004 },
      ];
      orbs.forEach((orb, i) => {
        const px = orb.fx * W + Math.sin(time * orb.s + i * 2) * 90;
        const py = orb.fy * H + Math.cos(time * orb.s + i)     * 70;
        const g  = ctx.createRadialGradient(px, py, 0, px, py, orb.r);
        g.addColorStop(0, `rgba(${orb.color},${orb.o})`);
        g.addColorStop(1, `rgba(${orb.color},0)`);
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(px, py, orb.r, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    function drawCircuits() {
      circuits.forEach(c => {
        c.pulse += c.speed;
        const alpha = (Math.sin(c.pulse) * 0.5 + 0.5) * 0.07 + 0.01;
        ctx.strokeStyle = `rgba(${c.color},${alpha})`;
        ctx.lineWidth   = 1;
        ctx.beginPath();
        if (c.dir === "h") {
          ctx.moveTo(c.x, c.y);
          ctx.lineTo(c.x + c.len, c.y);
        } else {
          ctx.moveTo(c.x, c.y);
          ctx.lineTo(c.x, c.y + c.len);
        }
        ctx.stroke();

        // Node dots
        ctx.fillStyle = `rgba(${c.color},${alpha * 2})`;
        ctx.beginPath();
        ctx.arc(c.x, c.y, 2, 0, Math.PI * 2);
        ctx.fill();
      });
    }

    function drawStreams() {
      const W = canvas.width, H = canvas.height;
      streams.forEach(s => {
        s.x += Math.cos(s.angle) * s.speed;
        s.y += Math.sin(s.angle) * s.speed;

        if (s.x < -50 || s.x > W+50 || s.y < -50 || s.y > H+50) {
          s.x = Math.random() * W;
          s.y = Math.random() * H;
          s.angle = Math.random() * Math.PI * 2;
          return; // Skip drawing this frame
        }

        const tailX = s.x - Math.cos(s.angle) * s.len;
        const tailY = s.y - Math.sin(s.angle) * s.len;

        // Safety check — NaN hone se error aata tha
        if (!isFinite(tailX) || !isFinite(tailY) ||
            !isFinite(s.x)   || !isFinite(s.y)) return;

        const grad = ctx.createLinearGradient(tailX, tailY, s.x, s.y);
        grad.addColorStop(0, `rgba(${s.color},0)`);
        grad.addColorStop(1, `rgba(${s.color},${s.o})`);
        ctx.beginPath();
        ctx.moveTo(tailX, tailY);
        ctx.lineTo(s.x, s.y);
        ctx.strokeStyle = grad;
        ctx.lineWidth   = 1;
        ctx.stroke();
      });
    }

    function drawHeartbeat() {
      const W = canvas.width, H = canvas.height;
      const y0 = H - 55;
      const steps = 180;
      const points = [];

      for (let i = 0; i < steps; i++) {
        const x   = (W / steps) * i;
        const t   = (i / steps) * Math.PI * 4 + time * 0.04;
        const mod = i % Math.floor(steps / 4);
        let y = y0;
        if      (mod === 10) y = y0 - 35;
        else if (mod === 11) y = y0 + 18;
        else if (mod === 12) y = y0 - 60;
        else if (mod === 13) y = y0 - 55;
        else if (mod === 14) y = y0 + 8;
        else                 y = y0 + Math.sin(t * 0.6) * 4;
        points.push({ x, y });
      }

      for (let i = 1; i < points.length; i++) {
        const prog  = i / points.length;
        const alpha = prog * 0.15;
        const blue  = Math.floor(prog * 255);
        ctx.beginPath();
        ctx.moveTo(points[i-1].x, points[i-1].y);
        ctx.lineTo(points[i].x,   points[i].y);
        ctx.strokeStyle = `rgba(0,${blue},255,${alpha})`;
        ctx.lineWidth   = 1.2;
        ctx.stroke();
      }
    }

    function drawConnections() {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx   = particles[i].x - particles[j].x;
          const dy   = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx*dx + dy*dy);
          if (dist < 110) {
            const alpha = (1 - dist / 110) * 0.08;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(0,229,255,${alpha})`;
            ctx.lineWidth   = 0.5;
            ctx.stroke();
          }
        }
      }
    }

    function updateParticles() {
      const W = canvas.width, H = canvas.height;
      particles.forEach(p => {
        const dx   = mouse.x - p.x;
        const dy   = mouse.y - p.y;
        const dist = Math.sqrt(dx*dx + dy*dy);

        if (dist < 180 && dist > 0) {
          const force = (1 - dist / 180) * 0.06;
          p.vx += (dx / dist) * force;
          p.vy += (dy / dist) * force;
        }

        p.vx *= 0.97; p.vy *= 0.97;
        p.x  += p.vx; p.y  += p.vy;

        if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
        if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;

        p.pulse += 0.04;
        const pulsed = p.o + Math.sin(p.pulse) * 0.07;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color},${pulsed})`;
        ctx.fill();
      });
    }

    function spawnExplosion(x, y) {
      for (let i = 0; i < 18; i++) {
        const angle = (Math.PI * 2 / 18) * i;
        const speed = Math.random() * 4 + 1.5;
        explosions.push({
          x, y,
          vx:    Math.cos(angle) * speed,
          vy:    Math.sin(angle) * speed,
          life:  1,
          r:     Math.random() * 3 + 1,
          color: COLORS[Math.floor(Math.random() * COLORS.length)],
        });
      }
    }

    function drawExplosions() {
      explosions = explosions.filter(e => e.life > 0);
      explosions.forEach(e => {
        e.x    += e.vx; e.y += e.vy;
        e.vx   *= 0.93; e.vy *= 0.93;
        e.life -= 0.025;
        ctx.beginPath();
        ctx.arc(e.x, e.y, e.r * e.life, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${e.color},${e.life * 0.8})`;
        ctx.fill();
      });
    }

    function drawCursorGlow() {
      if (mouse.x === -999) return;
      const r    = mouse.clicking ? 65 : 40;
      const g    = ctx.createRadialGradient(
        mouse.x, mouse.y, 0,
        mouse.x, mouse.y, r
      );
      g.addColorStop(0, `rgba(0,229,255,${mouse.clicking ? 0.14 : 0.07})`);
      g.addColorStop(1, "rgba(0,229,255,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(mouse.x, mouse.y, r, 0, Math.PI * 2);
      ctx.fill();
    }

    // ── Main loop ──
    function loop() {
      const W = canvas.width, H = canvas.height;
      if (!W || !H) { raf = requestAnimationFrame(loop); return; }

      ctx.clearRect(0, 0, W, H);
      time++;

      drawOrbs();
      drawCircuits();
      drawStreams();
      drawHeartbeat();
      drawConnections();
      updateParticles();
      drawExplosions();
      drawCursorGlow();

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
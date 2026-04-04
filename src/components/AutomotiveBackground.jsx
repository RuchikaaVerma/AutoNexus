import { useEffect, useRef } from "react";

export default function AutomotiveBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let W, H, t = 0, raf;
    let cars = [], particles = [], streaks = [], orbs = [];
    let mouseX = -999, mouseY = -999;

    const onMouse = (e) => { mouseX = e.clientX; mouseY = e.clientY; };
    window.addEventListener("mousemove", onMouse);

    function resize() {
      W = canvas.width = window.innerWidth;
      H = canvas.height = window.innerHeight;
      initAll();
    }

    function initAll() {
      cars = [];
      const laneXs = [W*0.28, W*0.38, W*0.50, W*0.62, W*0.72];
      laneXs.forEach((lx, i) => {
        cars.push({
          x: lx + (Math.random()-0.5)*20,
          y: -80 - i*140,
          speed: 2 + Math.random()*2,
          color: ['#ff2d55','#00e5ff','#ffb800','#9d4edd','#00ff9d'][i % 5],
          w: 26, h: 48
        });
      });
      for (let i = 0; i < 5; i++) cars.push({
        x: W*0.22 + Math.random()*W*0.56,
        y: Math.random()*H,
        speed: 1.5 + Math.random()*2.5,
        color: ['#ff2d55','#00e5ff','#ffb800','#9d4edd'][i % 4],
        w: 24, h: 46
      });

      particles = [];
      for (let i = 0; i < 90; i++) particles.push({
        x: Math.random()*W, y: Math.random()*H,
        vx: (Math.random()-0.5)*0.35, vy: (Math.random()-0.5)*0.35,
        r: Math.random()*1.6+0.3, o: Math.random()*0.35+0.1,
        color: ['0,229,255','0,255,157','255,184,0','255,45,85','157,78,221'][Math.floor(Math.random()*5)],
        pulse: Math.random()*Math.PI*2
      });

      streaks = [];
      for (let i = 0; i < 14; i++) streaks.push({
        x: W*0.18 + Math.random()*W*0.64,
        y: Math.random()*H,
        speed: 2.5 + Math.random()*4.5,
        len: 50 + Math.random()*90,
        o: 0.1 + Math.random()*0.2,
        color: i%3===0 ? '255,45,85' : i%3===1 ? '0,229,255' : '255,184,0'
      });

      orbs = [
        { fx:0.12, fy:0.3,  r:200, color:'0,229,255',  o:0.035, s:0.00035 },
        { fx:0.88, fy:0.6,  r:180, color:'157,78,221', o:0.028, s:0.00055 },
        { fx:0.5,  fy:0.85, r:160, color:'0,255,157',  o:0.025, s:0.00045 },
      ];
    }

    function drawGrid() {
      const spacing = 55;
      const offset = (t * 0.25) % spacing;
      ctx.strokeStyle = 'rgba(0,229,255,0.03)';
      ctx.lineWidth = 0.5;
      for (let x = -spacing+offset; x < W+spacing; x += spacing) {
        ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
      }
      for (let y = 0; y < H; y += spacing) {
        ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
      }
    }

    function drawOrbs() {
      orbs.forEach((ob, i) => {
        const px = ob.fx*W + Math.sin(t*ob.s + i*2)*85;
        const py = ob.fy*H + Math.cos(t*ob.s + i)*65;
        const g = ctx.createRadialGradient(px,py,0,px,py,ob.r);
        g.addColorStop(0, `rgba(${ob.color},${ob.o})`);
        g.addColorStop(1, `rgba(${ob.color},0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(px,py,ob.r,0,Math.PI*2); ctx.fill();
      });
    }

    function drawRoad() {
      const cx = W/2, vanY = H*0.14, roadW = W*0.9;
      ctx.fillStyle = 'rgba(3,8,20,0.97)';
      ctx.fillRect(0,0,W,H);
      ctx.beginPath();
      ctx.moveTo(cx-22,vanY); ctx.lineTo(cx+22,vanY);
      ctx.lineTo(cx+roadW/2,H); ctx.lineTo(cx-roadW/2,H);
      ctx.closePath();
      ctx.fillStyle = 'rgba(6,12,28,0.9)'; ctx.fill();

      for (let l = 1; l < 5; l++) {
        const fr = l/5;
        const x1 = cx+(fr-0.5)*40, x2 = cx+(fr-0.5)*roadW;
        for (let d = 0; d < 18; d++) {
          const py = vanY+(H-vanY)*(d/18);
          const ny = vanY+(H-vanY)*((d+0.42)/18);
          const px = x1+(x2-x1)*(d/18);
          const nx = x1+(x2-x1)*((d+0.42)/18);
          const tw = 1.2 + 4.5*(d/18);
          const pulsed = 0.05 + 0.12*Math.abs(Math.sin(t*0.035+d*0.5));
          ctx.beginPath(); ctx.moveTo(px,py); ctx.lineTo(nx,ny);
          ctx.strokeStyle = `rgba(0,229,255,${pulsed})`;
          ctx.lineWidth = tw; ctx.stroke();
        }
      }
    }

    function drawCar(car) {
      ctx.save();
      ctx.translate(car.x, car.y);
      const sc = 0.65 + 0.35*(Math.max(0,car.y)/H);
      ctx.scale(sc, sc);
      const { w, h, color } = car;

      ctx.fillStyle = 'rgba(6,12,28,0.92)';
      ctx.beginPath(); ctx.roundRect(-w/2,-h/2,w,h,6); ctx.fill();
      ctx.strokeStyle = color+'55'; ctx.lineWidth = 0.8; ctx.stroke();

      ctx.fillStyle = 'rgba(150,200,255,0.09)';
      ctx.beginPath(); ctx.roundRect(-w/2+3,-h/2+5,w-6,h*0.36,3); ctx.fill();

      ctx.fillStyle = color; ctx.globalAlpha = 0.95;
      ctx.beginPath(); ctx.ellipse(-w/2+5,h/2-7,4.5,2,0,0,Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(w/2-5,h/2-7,4.5,2,0,0,Math.PI*2); ctx.fill();

      const hg = ctx.createRadialGradient(0,-h/2-4,0,0,-h/2-4,22);
      hg.addColorStop(0,'rgba(255,245,190,0.55)');
      hg.addColorStop(1,'rgba(255,245,190,0)');
      ctx.globalAlpha = 0.55; ctx.fillStyle = hg;
      ctx.beginPath(); ctx.ellipse(0,-h/2-4,20,9,0,0,Math.PI*2); ctx.fill();
      ctx.globalAlpha = 1;
      ctx.restore();
    }

    function drawStreaks() {
      streaks.forEach(s => {
        s.y += s.speed;
        if (s.y > H+s.len) { s.y = -s.len; s.x = W*0.18+Math.random()*W*0.64; }
        if (!isFinite(s.x) || !isFinite(s.y)) return;
        const g = ctx.createLinearGradient(s.x, s.y-s.len, s.x, s.y);
        g.addColorStop(0, `rgba(${s.color},0)`);
        g.addColorStop(1, `rgba(${s.color},${s.o})`);
        ctx.beginPath(); ctx.moveTo(s.x, s.y-s.len); ctx.lineTo(s.x, s.y);
        ctx.strokeStyle = g; ctx.lineWidth = 1; ctx.stroke();
      });
    }

    function drawParticles() {
      particles.forEach(p => {
        const dx = mouseX-p.x, dy = mouseY-p.y;
        const dist = Math.sqrt(dx*dx+dy*dy);
        if (dist < 160 && dist > 0) {
          const f = (1-dist/160)*0.055;
          p.vx += (dx/dist)*f; p.vy += (dy/dist)*f;
        }
        p.vx *= 0.97; p.vy *= 0.97;
        p.x += p.vx; p.y += p.vy;
        if (p.x<0) p.x=W; if (p.x>W) p.x=0;
        if (p.y<0) p.y=H; if (p.y>H) p.y=0;
        p.pulse += 0.045;
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle = `rgba(${p.color},${p.o+Math.sin(p.pulse)*0.08})`;
        ctx.fill();
      });
    }

    function drawConnections() {
      for (let i = 0; i < particles.length; i++)
        for (let j = i+1; j < particles.length; j++) {
          const dx = particles[i].x-particles[j].x;
          const dy = particles[i].y-particles[j].y;
          const d = Math.sqrt(dx*dx+dy*dy);
          if (d < 105) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x,particles[i].y);
            ctx.lineTo(particles[j].x,particles[j].y);
            ctx.strokeStyle = `rgba(0,229,255,${(1-d/105)*0.07})`;
            ctx.lineWidth = 0.5; ctx.stroke();
          }
        }
    }

    function drawHeartbeat() {
      const y0 = H-50, steps = 200, pts = [];
      for (let i = 0; i < steps; i++) {
        const x = (W/steps)*i;
        const mod = i % Math.floor(steps/4);
        let y = y0;
        if      (mod===10) y = y0-32;
        else if (mod===11) y = y0+16;
        else if (mod===12) y = y0-55;
        else if (mod===13) y = y0-50;
        else if (mod===14) y = y0+8;
        else y = y0 + Math.sin((i/steps)*Math.PI*4+t*0.045)*4;
        pts.push({x,y});
      }
      for (let i = 1; i < pts.length; i++) {
        const prog = i/pts.length;
        ctx.beginPath();
        ctx.moveTo(pts[i-1].x, pts[i-1].y);
        ctx.lineTo(pts[i].x, pts[i].y);
        ctx.strokeStyle = `rgba(0,${Math.floor(prog*229)},255,${prog*0.16})`;
        ctx.lineWidth = 1.2; ctx.stroke();
      }
    }

    function loop() {
      if (!W || !H) { raf = requestAnimationFrame(loop); return; }
      ctx.clearRect(0,0,W,H);
      t++;
      drawGrid();
      drawOrbs();
      drawRoad();
      drawStreaks();
      cars.forEach(c => { c.y += c.speed; if (c.y > H+120) c.y = -120; drawCar(c); });
      drawConnections();
      drawParticles();
      drawHeartbeat();
      raf = requestAnimationFrame(loop);
    }

    resize();
    loop();
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", onMouse);
    };
  }, []);

  return (
    <canvas ref={canvasRef} style={{
      position: "fixed", inset: 0,
      width: "100%", height: "100%",
      zIndex: 0, pointerEvents: "none"
    }} />
  );
}
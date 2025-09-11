// Orbes de fondo
(() => {
  const c = document.getElementById('bg-orbs');
  if (!c) return;
  const ctx = c.getContext('2d');
  let W, H, orbs = [], raf;
  const N = 28;

  function resize(){
    W = c.width = window.innerWidth;
    H = c.height = window.innerHeight;
  }
  window.addEventListener('resize', resize); resize();

  function rnd(a,b){ return Math.random()*(b-a)+a; }

  function init(){
    orbs = [];
    for(let i=0;i<N;i++){
      orbs.push({
        x:rnd(0,W), y:rnd(0,H),
        vx:rnd(-0.4,0.4), vy:rnd(-0.4,0.4),
        r:rnd(18,60),
        hue:rnd(180,300),    
        alpha:rnd(0.08,0.16)
      });
    }
  }
  init();

  function tick(){
    ctx.clearRect(0,0,W,H);
    // conexiones
    for (let i=0;i<N;i++){
      for (let j=i+1;j<N;j++){
        const a=orbs[i], b=orbs[j];
        const dx=a.x-b.x, dy=a.y-b.y;
        const d = Math.hypot(dx,dy);
        if (d<150){
          ctx.strokeStyle = `rgba(124,77,255,${(150-d)/900})`;
          ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
        }
      }
    }
    // orbes
    for (const o of orbs){
      o.x+=o.vx; o.y+=o.vy;
      if(o.x< -50||o.x>W+50) o.vx*=-1;
      if(o.y< -50||o.y>H+50) o.vy*=-1;

      const g = ctx.createRadialGradient(o.x,o.y,0,o.x,o.y,o.r);
      g.addColorStop(0, `hsla(${o.hue}, 95%, 60%, ${o.alpha*1.2})`);
      g.addColorStop(1, `hsla(${o.hue}, 95%, 60%, 0)`);
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(o.x,o.y,o.r,0,Math.PI*2); ctx.fill();
    }
    raf = requestAnimationFrame(tick);
  }
  tick();
})();


function applyTilt(selector='.card-tilt'){
  const els = document.querySelectorAll(selector);
  els.forEach(el=>{
    el.addEventListener('mousemove', (e)=>{
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5;
      const y = (e.clientY - r.top) / r.height - .5;
      el.style.transform = `rotateX(${(-y*6)}deg) rotateY(${x*6}deg) translateY(-4px)`;
    });
    el.addEventListener('mouseleave', ()=>{ el.style.transform=''; });
  });
}
document.addEventListener('DOMContentLoaded', ()=>applyTilt());



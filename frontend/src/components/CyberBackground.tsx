import { useEffect, useRef, useState } from 'react';

export default function CyberBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [parallax, setParallax] = useState({ x: 0, y: 0 });

  // Interactive subtle mouse parallax
  useEffect(() => {
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;
    let animationId: number;

    const handleMouseMove = (e: MouseEvent) => {
      const { innerWidth, innerHeight } = window;
      targetX = (e.clientX / innerWidth - 0.5) * 20; // max 10px shift
      targetY = (e.clientY / innerHeight - 0.5) * 16; // max 8px shift
    };

    const animateParallax = () => {
      // Smooth lerp
      currentX += (targetX - currentX) * 0.05;
      currentY += (targetY - currentY) * 0.05;
      setParallax({ x: currentX, y: currentY });
      animationId = requestAnimationFrame(animateParallax);
    };

    window.addEventListener('mousemove', handleMouseMove);
    animationId = requestAnimationFrame(animateParallax);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      cancelAnimationFrame(animationId);
    };
  }, []);

  // Floating ambient atmospheric motes / sunlight breeze particles (Clean & Delicate, NO FOG)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let motes: { x: number; y: number; vx: number; vy: number; radius: number; alpha: number; pulseSpeed: number }[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initMotes();
    };

    const initMotes = () => {
      motes = [];
      const count = Math.floor(canvas.width / 35); // Delicate density
      for (let i = 0; i < count; i++) {
        motes.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.2) * 0.6, // Drift slowly to the right
          vy: -(0.2 + Math.random() * 0.5), // Gently float upwards
          radius: 1 + Math.random() * 2.2, // Tiny sparkling specks
          alpha: 0.15 + Math.random() * 0.45,
          pulseSpeed: 0.02 + Math.random() * 0.03,
        });
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < motes.length; i++) {
        const m = motes[i];
        m.x += m.vx;
        m.y += m.vy;

        // Wrap around boundaries
        if (m.y < -10) m.y = canvas.height + 10;
        if (m.x > canvas.width + 10) m.x = -10;
        if (m.x < -10) m.x = canvas.width + 10;

        ctx.beginPath();
        ctx.arc(m.x, m.y, m.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(235, 248, 255, ${m.alpha})`;
        ctx.shadowBlur = 8;
        ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
        ctx.fill();
        ctx.shadowBlur = 0; // reset
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener('resize', resize);
    resize();
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-[-1] overflow-hidden bg-[#030712]">
      {/* 8K Full Mountain Landscape with Cinematic Drift Motion & Mouse Parallax */}
      <div 
        className="absolute w-[108%] h-[108%] -top-[4%] -left-[4%] animate-cinematic-drift transition-transform duration-150 ease-out"
        style={{
          backgroundImage: 'url(/mountain_bg.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center 40%',
          backgroundRepeat: 'no-repeat',
          transform: `translate3d(${parallax.x}px, ${parallax.y}px, 0)`
        }}
      />
      
      {/* Dynamic Sunbeam Light Sweep Across the Sky & Peaks */}
      <div 
        className="absolute -top-1/4 left-1/4 w-[120%] h-[90%] pointer-events-none mix-blend-screen animate-sun-shimmer"
        style={{
          background: 'radial-gradient(ellipse at 40% 20%, rgba(255, 250, 220, 0.35) 0%, rgba(255, 255, 255, 0.15) 30%, transparent 65%)',
        }}
      />

      {/* Ambient Sparkling Mountain Air Breeze Particles */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none mix-blend-screen opacity-70"
      />

      {/* Gentle Edge Vignette to preserve UI contrast without obstructing mountain center */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{ 
          background: 'linear-gradient(to bottom, rgba(2, 6, 23, 0.3) 0%, transparent 25%, transparent 70%, rgba(2, 6, 23, 0.5) 100%)' 
        }}
      />
    </div>
  );
}

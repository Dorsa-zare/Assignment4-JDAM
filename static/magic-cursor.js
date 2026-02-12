(() => {
    const canvas = document.getElementById("magic-cursor");
    if (!canvas) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reducedMotion) {
        canvas.style.display = "none";
        return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const particles = [];
    const cpuHint = Math.max(2, Math.min(8, navigator.hardwareConcurrency || 4));
    const maxParticles = cpuHint <= 4 ? 70 : 100;
    const minSpawnGap = cpuHint <= 4 ? 12 : 8;
    const pointer = {
        x: window.innerWidth / 2,
        y: window.innerHeight / 2,
        lastX: window.innerWidth / 2,
        lastY: window.innerHeight / 2,
        active: false,
        spawnCarry: 0
    };

    const palette = ["#47d6ff", "#9a6cff", "#ff9fd4", "#e8deff"];

    const setCanvasSize = () => {
        const dpr = window.devicePixelRatio || 1;
        canvas.width = Math.floor(window.innerWidth * dpr);
        canvas.height = Math.floor(window.innerHeight * dpr);
        canvas.style.width = `${window.innerWidth}px`;
        canvas.style.height = `${window.innerHeight}px`;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const spawnParticle = (x, y, speedScale) => {
        const angle = Math.random() * Math.PI * 2;
        const speed = (0.35 + Math.random() * 1.15) * speedScale;
        particles.push({
            x,
            y,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed - 0.18,
            radius: 1 + Math.random() * 1.8,
            life: 20 + Math.random() * 20,
            maxLife: 40,
            color: palette[Math.floor(Math.random() * palette.length)]
        });

        if (particles.length > maxParticles) {
            particles.shift();
        }
    };

    const drawWandCore = () => {
        const gradient = ctx.createRadialGradient(pointer.x, pointer.y, 0, pointer.x, pointer.y, 20);
        gradient.addColorStop(0, "rgba(255, 255, 255, 0.95)");
        gradient.addColorStop(0.4, "rgba(71, 214, 255, 0.7)");
        gradient.addColorStop(1, "rgba(71, 214, 255, 0)");
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(pointer.x, pointer.y, 20, 0, Math.PI * 2);
        ctx.fill();
    };

    const tick = () => {
        if (!pointer.active && particles.length === 0) {
            requestAnimationFrame(tick);
            return;
        }

        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

        if (pointer.active) {
            const dx = pointer.x - pointer.lastX;
            const dy = pointer.y - pointer.lastY;
            const distance = Math.hypot(dx, dy);
            pointer.spawnCarry += distance;
            const speedScale = Math.min(1.5, 0.75 + distance * 0.015);

            const emitCount = Math.floor(pointer.spawnCarry / minSpawnGap);
            if (emitCount > 0 && distance > 0) {
                for (let i = 0; i < emitCount; i += 1) {
                    const t = (i + 1) / (emitCount + 1);
                    const px = pointer.lastX + dx * t;
                    const py = pointer.lastY + dy * t;
                    spawnParticle(px, py, speedScale);
                }
                pointer.spawnCarry -= emitCount * minSpawnGap;
            }

            pointer.lastX = pointer.x;
            pointer.lastY = pointer.y;
        }

        for (let i = particles.length - 1; i >= 0; i -= 1) {
            const p = particles[i];
            p.life -= 1;
            if (p.life <= 0) {
                particles.splice(i, 1);
                continue;
            }

            p.x += p.vx;
            p.y += p.vy;
            p.vx *= 0.98;
            p.vy *= 0.985;
            p.vy += 0.014;

            const alpha = p.life / p.maxLife;
            ctx.globalCompositeOperation = "screen";
            ctx.fillStyle = `${p.color}${Math.floor(alpha * 255).toString(16).padStart(2, "0")}`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.globalCompositeOperation = "lighter";
        drawWandCore();
        ctx.globalCompositeOperation = "source-over";

        requestAnimationFrame(tick);
    };

    window.addEventListener("resize", setCanvasSize);

    window.addEventListener("pointermove", (event) => {
        pointer.active = true;
        pointer.x = event.clientX;
        pointer.y = event.clientY;
    });

    window.addEventListener("pointerleave", () => {
        pointer.active = false;
    });

    setCanvasSize();
    requestAnimationFrame(tick);
})();

let canvas = null;
let ctx = null;
let animationId = null;
let particles = [];
let isActive = false;
let resizeListener = null;

const PARTICLE_COUNT = 45;
const PARTICLE_COLORS = [
    "rgba(109, 121, 242, 0.55)",
    "rgba(150, 140, 255, 0.40)",
    "rgba(190, 185, 255, 0.35)",
    "rgba(255, 255, 255, 0.25)",
];

function createParticle(spreadY = false) {
    return {
        x: Math.random() * canvas.width,
        y: spreadY ? Math.random() * canvas.height : canvas.height + Math.random() * 30,
        size: Math.random() * 4 + 1.5,
        speedX: (Math.random() - 0.5) * 0.6,
        speedY: -(Math.random() * 1.2 + 0.4),
        color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
    };
}

function initParticles() {
    particles = Array.from({ length: PARTICLE_COUNT }, () => createParticle(true));
}

function updateParticles() {
    for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.speedX;
        p.y += p.speedY;
        if (p.y < -10) {
            particles[i] = createParticle(false);
        }
    }
}

function drawParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of particles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();
    }
}

function loop() {
    if (!isActive) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        animationId = null;
        return;
    }
    updateParticles();
    drawParticles();
    animationId = requestAnimationFrame(loop);
}

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    if (isActive) {
        drawParticles();
    }
}

export function initParticleSystem() {
    canvas = document.querySelector("#particles-canvas");
    ctx = canvas.getContext("2d");
    resizeCanvas();
    resizeListener = resizeCanvas;
    window.addEventListener("resize", resizeListener);
    initParticles();
}

export function destroyParticleSystem() {
    if (resizeListener) {
        window.removeEventListener("resize", resizeListener);
        resizeListener = null;
    }
    isActive = false;
    animationId = null;
}

export function setParticlesActive(active) {
    if (isActive === active) return;
    isActive = active;
    if (active && animationId === null) {
        loop();
    }
}

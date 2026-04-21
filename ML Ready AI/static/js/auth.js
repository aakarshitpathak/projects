// Toggle Forms
function showSignup() {
    document.getElementById("loginForm").style.display = "none";
    document.getElementById("signupForm").style.display = "block";
}

function showLogin() {
    document.getElementById("loginForm").style.display = "block";
    document.getElementById("signupForm").style.display = "none";
}

// ===== YOUR NEURAL NETWORK BACKGROUND =====

const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');

let W, H, nodes, edges;

function rand(min, max) {
    return Math.random() * (max - min) + min;
}

function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
    init();
}

function init() {
    const layers = [3, 5, 6, 5, 3];
    nodes = [];
    edges = [];

    const xStep = W / (layers.length + 1);

    layers.forEach((count, li) => {
        const x = xStep * (li + 1);
        const yStep = H / (count + 1);

        for (let i = 0; i < count; i++) {
            nodes.push({
                x,
                y: yStep * (i + 1),
                layer: li
            });
        }
    });

    for (let li = 0; li < layers.length - 1; li++) {
        const from = nodes.filter(n => n.layer === li);
        const to = nodes.filter(n => n.layer === li + 1);

        from.forEach(f => {
            to.forEach(t => {
                edges.push({ from: f, to: t });
            });
        });
    }
}

function draw() {
    ctx.clearRect(0, 0, W, H);

    // Draw edges
    ctx.strokeStyle = "rgba(0,229,255,0.2)";
    edges.forEach(e => {
        ctx.beginPath();
        ctx.moveTo(e.from.x, e.from.y);
        ctx.lineTo(e.to.x, e.to.y);
        ctx.stroke();
    });

    // Draw nodes
    nodes.forEach(n => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = "#00e5ff";
        ctx.fill();
    });

    requestAnimationFrame(draw);
}

window.addEventListener('resize', resize);

resize();
draw();
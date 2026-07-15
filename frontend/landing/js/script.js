const TARGETS = {
    workspace: 'http://localhost:5173',
    dashboard: 'http://localhost:8501'
};

function setupNavigation() {
    document.querySelectorAll('.card[data-target]').forEach(card => {
        card.addEventListener('click', e => {
            e.preventDefault();
            const url = TARGETS[card.dataset.target];
            if (url) window.open(url, '_blank');
        });
    });
}

function setupTiltEffect() {
    const cards = document.querySelectorAll('.card, .console');

    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -3.5;
            const rotateY = ((x - centerX) / centerX) * 3.5;

            card.style.transform =
                `translateY(-4px) perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

function setupMagneticButtons() {
    const buttons = document.querySelectorAll('.card-cta');
    const radius = 70;
    const strength = 0.35;

    document.addEventListener('mousemove', e => {
        buttons.forEach(btn => {
            const rect = btn.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;
            const dx = e.clientX - cx;
            const dy = e.clientY - cy;
            const dist = Math.hypot(dx, dy);

            if (dist < radius) {
                const pull = 1 - dist / radius;
                btn.style.transform = `translate(${dx * strength * pull}px, ${dy * strength * pull}px)`;
            } else {
                btn.style.transform = '';
            }
        });
    });
}

function setupRipple() {
    document.querySelectorAll('.card-cta').forEach(cta => {
        cta.addEventListener('click', e => {
            const rect = cta.getBoundingClientRect();
            const ripple = document.createElement('span');
            const size = Math.max(rect.width, rect.height);
            ripple.className = 'ripple';
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
            ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
            cta.appendChild(ripple);
            ripple.addEventListener('animationend', () => ripple.remove());
        });
    });
}

function setupScrollReveal() {
    const targets = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

    targets.forEach(el => observer.observe(el));
}

function setupConsoleFeed() {
    const body = document.getElementById('console-body');
    if (!body) return;

    const lines = [
        { tag: 'planner', text: 'decomposing query into 4 subtopics' },
        { tag: 'retriever', text: 'scanning sources across the web' },
        { tag: 'analyst', text: 'cross-referencing findings' },
        { tag: 'synthesizer', text: 'drafting citations and structure' },
        { tag: 'report', text: 'ready for review and export' }
    ];

    let lineIndex = 0;
    let charIndex = 0;
    let currentEl = null;
    const typeSpeed = 26;
    const holdTime = 900;
    const lineGap = 260;

    function typeChar() {
        const line = lines[lineIndex];
        if (charIndex === 0) {
            currentEl = document.createElement('div');
            currentEl.className = 'console-line';
            currentEl.innerHTML = `<span class="tag">${line.tag} →</span><span class="txt"></span><span class="caret"></span>`;
            body.appendChild(currentEl);
            while (body.children.length > 5) {
                body.removeChild(body.firstChild);
            }
        }

        const txtSpan = currentEl.querySelector('.txt');
        if (charIndex < line.text.length) {
            txtSpan.textContent += line.text[charIndex];
            charIndex++;
            setTimeout(typeChar, typeSpeed);
        } else {
            currentEl.querySelector('.caret').remove();
            charIndex = 0;
            lineIndex = (lineIndex + 1) % lines.length;
            setTimeout(typeChar, lineIndex === 0 ? holdTime + 400 : lineGap);
        }
    }

    setTimeout(typeChar, 500);
}

function setupSwarmCanvas() {
    const canvas = document.getElementById('swarm-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width, height, nodes;
    const NODE_COUNT = 26;
    const LINK_DIST = 150;
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = Math.min(window.innerHeight * 0.9, 900);
        canvas.style.height = `${height}px`;
    }

    function makeNodes() {
        nodes = Array.from({ length: NODE_COUNT }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            vx: (Math.random() - 0.5) * 0.25,
            vy: (Math.random() - 0.5) * 0.25
        }));
    }

    function step() {
        ctx.clearRect(0, 0, width, height);

        nodes.forEach(n => {
            n.x += n.vx;
            n.y += n.vy;
            if (n.x < 0 || n.x > width) n.vx *= -1;
            if (n.y < 0 || n.y > height) n.vy *= -1;
        });

        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const a = nodes[i], b = nodes[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < LINK_DIST) {
                    ctx.strokeStyle = `rgba(13, 148, 136, ${0.12 * (1 - dist / LINK_DIST)})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            }
        }

        nodes.forEach(n => {
            ctx.fillStyle = 'rgba(13, 148, 136, 0.35)';
            ctx.beginPath();
            ctx.arc(n.x, n.y, 1.8, 0, Math.PI * 2);
            ctx.fill();
        });

        if (!prefersReduced) requestAnimationFrame(step);
    }

    resize();
    makeNodes();
    step();

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            resize();
            makeNodes();
            if (prefersReduced) step();
        }, 200);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupTiltEffect();
    setupRipple();
    setupMagneticButtons();
    setupScrollReveal();
    setupConsoleFeed();
    setupSwarmCanvas();
});
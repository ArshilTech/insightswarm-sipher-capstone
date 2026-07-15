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
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -4;
            const rotateY = ((x - centerX) / centerX) * 4;

            card.style.transform =
                `translateY(-4px) perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupTiltEffect();
});

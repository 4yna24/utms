document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-button');
    const jumpButtons = document.querySelectorAll('.tab-jump');
    const panels = document.querySelectorAll('.workspace-panel');

    if (!tabButtons.length || !panels.length) {
        return;
    }

    const activatePanel = (targetId) => {
        panels.forEach((panel) => {
            panel.classList.toggle('active', panel.id === targetId);
        });

        tabButtons.forEach((button) => {
            const isActive = button.dataset.target === targetId;
            button.classList.toggle('active', isActive);
            button.setAttribute('aria-pressed', String(isActive));
        });
    };

    tabButtons.forEach((button) => {
        button.addEventListener('click', () => activatePanel(button.dataset.target));
    });

    jumpButtons.forEach((button) => {
        button.addEventListener('click', () => activatePanel(button.dataset.target));
    });
});

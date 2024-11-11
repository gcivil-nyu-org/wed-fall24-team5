document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('org-modal');
    const openModalButton = document.getElementById('open-modal');

    // Function to open the modal
    openModalButton.addEventListener('click', () => {
        modal.classList.add('is-active');
    });
});

function closeModal() {
    const modal = document.getElementById('org-modal');
    modal.classList.remove('is-active');
}
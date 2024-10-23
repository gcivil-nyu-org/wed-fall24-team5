document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('org-modal');
    const openModalButton = document.getElementById('open-modal');
    const closeModalFooterButton = document.getElementById('close-modal-footer');
    const modalBackground = document.getElementById('modal-background');

    // Function to open the modal
    openModalButton.addEventListener('click', () => {
        modal.classList.add('is-active');
    });

    // Function to close the modal
    const closeModal = () => {
        modal.classList.remove('is-active');
    };

    // Close the modal on clicking the cancel button in footer
    closeModalFooterButton.addEventListener('click', (event) => {
        event.preventDefault();
        closeModal();
    });

    // Close the modal on clicking outside the modal (on the background)
    modalBackground.addEventListener('click', closeModal);
});

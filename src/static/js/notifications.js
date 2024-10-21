// Auto-dismiss notification after 10 seconds
document.addEventListener('DOMContentLoaded', () => {
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(notification => {
        setTimeout(() => {
            notification.style.display = 'none';
        }, 10000);
    });

    // Enable close button on notification
    const closeButtons = document.querySelectorAll('.delete');
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            button.parentElement.style.display = 'none';
        });
    });
});
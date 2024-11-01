
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching functionality and remember what tab
    // we are on by using localStorage
    const tabs = document.querySelectorAll('.tabs ul li');
    const orderLists = document.querySelectorAll('.order-list');

    // Get the active tab from localStorage, if available
    const savedTab = localStorage.getItem('activeTab') || 'pending-tab';

    // Set the active tab based on savedTab
    tabs.forEach((tab, index) => {
        if (tab.id === savedTab) {
            tab.classList.add('is-active');
            orderLists[index].classList.remove('is-hidden');
        } else {
            tab.classList.remove('is-active');
            orderLists[index].classList.add('is-hidden');
        }
    });

    // Add click event listeners to tabs
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Set active class on the selected tab and remove from others
            tabs.forEach(t => t.classList.remove('is-active'));
            orderLists.forEach(list => list.classList.add('is-hidden'));

            tab.classList.add('is-active');
            orderLists[index].classList.remove('is-hidden');

            // Save the selected tab in localStorage
            localStorage.setItem('activeTab', tab.id);
        });
    });

    // Modal functionality
    const modal = document.getElementById('modifyOrderModal');
    const closeButtons = modal.querySelectorAll('.delete, .modal-background');

    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            closeModifyModal();
        });
    });
});

// Modal functions
function openModifyModal(orderId, currentQuantity, availableQuantity, foodItem) {
    const modal = document.getElementById('modifyOrderModal');
    const maxAllowed = Math.min(3, parseInt(availableQuantity) + parseInt(currentQuantity));

    document.getElementById('order_id').value = orderId;
    document.getElementById('current_quantity').value = currentQuantity;
    document.getElementById('available_quantity').value = availableQuantity;
    document.getElementById('food_item').value = foodItem;
    document.getElementById('new_quantity').max = maxAllowed;
    document.getElementById('max_allowed').textContent = maxAllowed;
    document.getElementById('new_quantity').value = currentQuantity;

    modal.classList.add('is-active');
}

function closeModifyModal() {
    const modal = document.getElementById('modifyOrderModal');
    modal.classList.remove('is-active');
}
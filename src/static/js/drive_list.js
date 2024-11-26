document.addEventListener('DOMContentLoaded', () => {
    // Tab switching functionality and remember what tab we are on by using localStorage
    const tabs = document.querySelectorAll('.tabs ul li');
    const driveLists = document.querySelectorAll('.drive-list');

    // Get the active tab from localStorage or default to 'pending-tab'
    const savedTab = localStorage.getItem('activeTab') || 'all-drives-tab';

    // Check if the savedTab matches any tab, otherwise default to 'pending-tab'
    let activeTabExists = false;
    tabs.forEach((tab, index) => {
        if (tab.id === savedTab) {
            tab.classList.add('is-active');
            driveLists[index].classList.remove('is-hidden');
            activeTabExists = true;
        } else {
            tab.classList.remove('is-active');
            driveLists[index].classList.add('is-hidden');
        }
    });

    // If no matching tab was found, set 'pending-tab' as the default active tab and show its content
    if (!activeTabExists) {
        const defaultTab = document.getElementById('all-drives-tab');
        const defaultContent = document.getElementById('pending-orders');

        if (defaultTab && defaultContent) {
            defaultTab.classList.add('is-active');
            defaultContent.classList.remove('is-hidden');
        }
    }

    // Add click event listeners to tabs
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and hide all order lists
            tabs.forEach(t => t.classList.remove('is-active'));
            driveLists.forEach(list => list.classList.add('is-hidden'));

            // Activate the selected tab and show the corresponding content
            tab.classList.add('is-active');
            driveLists[index].classList.remove('is-hidden');

            // Save the selected tab in localStorage
            localStorage.setItem('activeTab', tab.id);
        });
    });

    function openModal($el) {
        $el.classList.add('is-active');
    }

    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    function closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(($modal) => {
            closeModal($modal);
        });
    }

    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.open-modal') || []).forEach(($trigger) => {
        const modal = $trigger.dataset.target;
        const $target = document.getElementById(modal);

        $trigger.addEventListener('click', () => {
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .is-delete, .close-btn') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeAllModals();
        }
    });
});

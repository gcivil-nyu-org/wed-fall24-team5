document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tabs ul li');
    const orgLists = document.querySelectorAll('.org-list');

    // Retrieve the active tab from localStorage, defaulting to 'active-tab'
    const savedTab = localStorage.getItem('activeTab') || 'active-tab';

    // Set the active tab based on savedTab
    tabs.forEach((tab, index) => {
        if (tab.id === savedTab) {
            tab.classList.add('is-active');
            orgLists[index].classList.remove('is-hidden');
        } else {
            tab.classList.remove('is-active');
            orgLists[index].classList.add('is-hidden');
        }
    });

    // Add click event listeners to tabs
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and hide all org lists
            tabs.forEach(t => t.classList.remove('is-active'));
            orgLists.forEach(list => list.classList.add('is-hidden'));

            // Add active class to the selected tab and show corresponding org list
            tab.classList.add('is-active');
            orgLists[index].classList.remove('is-hidden');

            // Save the selected tab in localStorage
            localStorage.setItem('activeTab', tab.id);
        });
    });
});
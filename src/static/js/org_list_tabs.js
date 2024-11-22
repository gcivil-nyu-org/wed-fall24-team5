document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tabs ul li');
    const orgLists = document.querySelectorAll('.org-list');

    // Retrieve the active tab from localStorage or default to 'active-tab'
    const savedTab = localStorage.getItem('activeTab') || 'active-tab';

    // Check if the savedTab matches any tab, otherwise default to 'active-tab'
    let activeTabExists = false;
    tabs.forEach((tab, index) => {
        if (tab.id === savedTab) {
            tab.classList.add('is-active');
            orgLists[index].classList.remove('is-hidden');
            activeTabExists = true;
        } else {
            tab.classList.remove('is-active');
            orgLists[index].classList.add('is-hidden');
        }
    });

    // If no matching tab was found, set 'active-tab' as the default active tab and show its content
    if (!activeTabExists) {
        const defaultTab = document.getElementById('active-tab');
        const defaultContent = document.querySelector('#active-tab.org-list');

        if (defaultTab && defaultContent) {
            defaultTab.classList.add('is-active');
            defaultContent.classList.remove('is-hidden');
        }
    }

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

    document.querySelectorAll('.short-text').forEach(element => {
        const maxChars = 35;
        if (element.textContent.length > maxChars) {
            element.textContent = element.textContent.slice(0, maxChars) + '...';
        }
    });
});
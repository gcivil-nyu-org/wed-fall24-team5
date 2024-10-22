// Auto-dismiss notification after 10 seconds
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tabs ul li');
    const orderLists = document.querySelectorAll('.org-list');

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('is-active'));
            orderLists.forEach(list => list.classList.add('is-hidden'));

            tab.classList.add('is-active');
            orderLists[index].classList.remove('is-hidden');
        });
    });
});
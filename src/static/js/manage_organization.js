document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll('.tabs ul li');
    const tabContents = document.querySelectorAll('.manage-tab');

    // Retrieve the active tab from localStorage or default to 'donations-tab'
    const savedTab = localStorage.getItem('activeTab') || 'donations-tab';

    // Check if the savedTab matches any tab, otherwise default to 'donations-tab'
    let activeTabExists = false;
    tabs.forEach((tab, index) => {
        if (tab.id === savedTab) {
            tab.classList.add('is-active');
            tabContents[index].classList.remove('is-hidden');
            activeTabExists = true;
        } else {
            tab.classList.remove('is-active');
            tabContents[index].classList.add('is-hidden');
        }
    });

    // If no matching tab was found, set 'donations-tab' as the default active tab and show its content
    if (!activeTabExists) {
        const defaultTab = document.getElementById('donations-tab');
        const defaultContent = document.getElementById('donations-content');

        if (defaultTab && defaultContent) {
            defaultTab.classList.add('is-active');
            defaultContent.classList.remove('is-hidden');
        }
    }

    // Add click event listeners to tabs
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and hide all tab contents
            tabs.forEach(t => t.classList.remove('is-active'));
            tabContents.forEach(content => content.classList.add('is-hidden'));

            // Activate the selected tab and show the corresponding content
            tab.classList.add('is-active');
            tabContents[index].classList.remove('is-hidden');

            // Save the selected tab in localStorage
            localStorage.setItem('activeTab', tab.id);
        });
    });

    // Existing code for modals, delete confirmation, etc.
    var addDonationButton = document.getElementById("add-donation-button");
    if (addDonationButton) {
        addDonationButton.onclick = function () {
            const modalHeader = document.getElementById('modal-header');
            modalHeader.textContent = 'Add a Donation';
            const organizationId = document.getElementById('organization-id').innerHTML;
            document.querySelector('input[name="food_item"]').value = "";
            document.querySelector('input[name="quantity"]').value = "";
            document.querySelector('input[name="pickup_by"]').value = "";
            document.querySelector('input[name="organization"]').value = organizationId;

            const modalForm = document.querySelector('#addDonationModal form');
            modalForm.action = `/donor_dashboard/add_donation/`;
            document.getElementById("addDonationModal").style.display = "block";
        };
    }

    const editLinks = document.querySelectorAll('.edit-link');
    editLinks.forEach(link => {
        link.onclick = function () {
            const modalHeader = document.getElementById('modal-header');
            modalHeader.textContent = 'Modify Donation';
            const donationId = this.getAttribute('data-id');
            const foodItem = this.getAttribute('data-food-item');
            const quantity = this.getAttribute('data-quantity');
            const pickupBy = this.getAttribute('data-pickup-by');
            const organizationId = document.getElementById('organization-id').innerHTML;

            document.querySelector('input[name="food_item"]').value = foodItem;
            document.querySelector('input[name="quantity"]').value = quantity;
            document.querySelector('input[name="pickup_by"]').value = pickupBy;
            document.querySelector('input[name="organization"]').value = organizationId;

            const modalForm = document.querySelector('#addDonationModal form');
            modalForm.action = `/donor_dashboard/modify_donation/${donationId}/`;

            const modal = document.getElementById('addDonationModal');
            modal.style.display = 'block';
        };
    });

    var closeButton = document.getElementById("closeModal");
    if (closeButton) {
        closeButton.onclick = function () {
            document.getElementById("addDonationModal").style.display = "none";
        };
    }

    window.onclick = function (event) {
        var modal = document.getElementById("addDonationModal");
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
});

document.addEventListener("DOMContentLoaded", function () {
    // Handle the tab switching logic
    const tabs = document.querySelectorAll('.tabs ul li');
    const donationsContent = document.getElementById('donations-content');
    const ordersContent = document.getElementById('orders-content');
    const reviewsContent = document.getElementById('reviews-content');

    function clearActiveTabs() {
        tabs.forEach(tab => {
            tab.classList.remove('is-active');
        });
        donationsContent.classList.add('is-hidden');
        ordersContent.classList.add('is-hidden');
        reviewsContent.classList.add('is-hidden');
    }

    // Add event listeners for the tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            clearActiveTabs();
            this.classList.add('is-active');
            // Show the content based on the clicked tab's id
            if (this.id === 'donations-tab') {
                donationsContent.classList.remove('is-hidden');
            } else if (this.id === 'orders-tab') {
                ordersContent.classList.remove('is-hidden');
            } else if (this.id === 'reviews-tab') {
                reviewsContent.classList.remove('is-hidden');
            }
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

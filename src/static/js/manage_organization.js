function confirmDelete() {
    if (confirm("Are you sure you want to delete this organization?")) {
        document.getElementById("delete-form").submit();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var addDonationButton = document.getElementById("add-donation-button");
    if (addDonationButton) {
        addDonationButton.onclick = function() {
            const modalHeader = document.getElementById('modal-header');
            modalHeader.textContent = 'Add a Donation'; 
            const organizationId =  document.getElementById('organization-id').innerHTML;
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
        link.onclick = function() {
            const modalHeader = document.getElementById('modal-header');
            modalHeader.textContent = 'Modify Donation'; 
            const donationId = this.getAttribute('data-id');
            const foodItem = this.getAttribute('data-food-item');
            const quantity = this.getAttribute('data-quantity');
            const pickupBy = this.getAttribute('data-pickup-by');
            const organizationId =  document.getElementById('organization-id').innerHTML;

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
        closeButton.onclick = function() {
            document.getElementById("addDonationModal").style.display = "none";
        };
    }

    // Clicking anywhere outside the modal closes it
    window.onclick = function(event) {
        var modal = document.getElementById("addDonationModal");
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
});

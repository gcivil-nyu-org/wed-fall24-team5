function confirmDelete() {
    if (confirm("Are you sure you want to delete this organization?")) {
        document.getElementById("delete-form").submit();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    var addDonationButton = document.getElementById("add-donation-button");
    
    // Ensure the element exists before assigning onclick
    if (addDonationButton) {
        addDonationButton.onclick = function() {
            document.getElementById("addDonationModal").style.display = "block";
        };
    }
    
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

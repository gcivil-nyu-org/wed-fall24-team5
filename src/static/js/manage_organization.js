// Function to confirm deletion of an organization
function confirmDelete() {
    if (confirm("Are you sure you want to make this organization inactive? All the donations and orders under this organization will also be inactive!!")) {
        // If confirmed, submit the form
        document.getElementById('delete-form').submit();
    }
}

// Function to confirm deletion of a donation and submit the form
function submitDeleteForm(donationId) {
    if (confirm("Are you sure you want to delete this donation?")) {
        // Find the form by ID and submit it
        document.getElementById('delete-form-' + donationId).submit();
    }
}

// Handle the dropdowns
document.addEventListener('DOMContentLoaded', function () {
    // Get all dropdown buttons
    const dropdownButtons = document.querySelectorAll('.orders-dropdown-trigger');

    dropdownButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            const isCurr = this.classList.contains('is-active');
            e.preventDefault();
            dropdownButtons.forEach(b => b.classList.remove('is-active'));
            const dropdownContent = this.closest('.orders-dropdown').querySelector('.orders-dropdown-content');

            // Close all other dropdowns
            document.querySelectorAll('.orders-dropdown-content').forEach(content => {
                if (content !== dropdownContent) {
                    content.classList.remove('is-active');
                    content.classList.add('is-hidden');
                }
            });

            if (isCurr) {
                // Close active dropdown
                dropdownContent.classList.remove('is-active');
                dropdownContent.classList.add('is-hidden');
                this.classList.remove('is-active');
            } else {
                // Toggle current dropdown
                dropdownContent.classList.remove('is-hidden');
                dropdownContent.classList.add('is-active');

                // Toggle button active state
                this.classList.add('is-active');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.closest('.orders-dropdown')) {
            document.querySelectorAll('.orders-dropdown-content').forEach(content => {
                content.classList.remove('is-active');
                content.classList.add('is-hidden');
            });
            document.querySelectorAll('.orders-dropdown-trigger').forEach(trigger => {
                trigger.classList.remove('is-active');
            });
        }
    });
});

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

    // Toggle dropdowns for donations with reviews
    const donationDropdowns = document.querySelectorAll('.donation-dropdown-trigger');

    donationDropdowns.forEach(trigger => {
        trigger.addEventListener('click', function () {
            const content = this.nextElementSibling;
            const icon = this.querySelector('.icon i');

            content.classList.toggle('is-hidden');
            icon.classList.toggle('fa-angle-down');
            icon.classList.toggle('fa-angle-up');
        });
    });


    const submitButton = document.querySelector('button[type="submit"]');

    // Existing code for modals, delete confirmation, etc.
    const quantityInput = document.getElementById("id_quantity");
    const quantityWarning = document.getElementById("quantity-warning");
    quantityInput.addEventListener("input", function () {
        const quantityValue = quantityInput.value;
        if (quantityValue <= 0 || quantityValue > 200) {
            quantityWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            quantityWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    const foodItemInput = document.getElementById("id_food_item");
    const foodItemWarning = document.getElementById("donation-name-warning");
    foodItemInput.addEventListener("input", function () {
        const foodItemValue = foodItemInput.value;
        if (foodItemValue.length > 250 || foodItemValue.length === 0) {
            foodItemWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            foodItemWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    const dateInput = document.getElementById("id_pickup_by");
    const dateWarning = document.getElementById("date-warning");
    dateInput.addEventListener("input", function () {
        const dateValue = dateInput.value;
        if (!isValidDate(dateValue)) {
            dateWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            dateWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    function isValidDate(dateString) {
        if (!dateString) return false;

        const inputDate = new Date(`${dateString}T00:00:00`);
        if (isNaN(inputDate)) return false;

        const currentDate = new Date();
        currentDate.setHours(0, 0, 0, 0); // Normalize to start of the day

        const range = new Date();
        range.setDate(currentDate.getDate() + 7);
        range.setHours(23, 59, 59, 999); // End of the range day

        return inputDate >= currentDate && inputDate <= range;
    }

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
            // document.getElementById("addDonationModal").style.display = "block";
            document.getElementById("addDonationModal").classList.add("is-active");
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

            document.getElementById("addDonationModal").classList.add("is-active");
        };
    });

    var closeButton = document.getElementById("closeModal");
    if (closeButton) {
        closeButton.onclick = function () {
            document.getElementById("addDonationModal").classList.remove("is-active");
        };
    }

    window.onclick = function (event) {
        var modal = document.getElementById("addDonationModal");
        if (event.target == modal) {
            modal.classList.remove("is-active");
        }
    };
});

document.addEventListener("DOMContentLoaded", () => {
    const images = document.querySelectorAll(".image.is-clickable");
    images.forEach(image => {
        image.addEventListener("click", () => {
            const donationId = image.getAttribute("data-donation-id");
            triggerFileUpload(donationId);
        });
    });
});


function triggerFileUpload(donationId) {
    document.getElementById(`file-upload-${donationId}`).click();
}

// Handle file upload and send to the server
function uploadDonationImage(inputElement) {
    const donationId = inputElement.dataset.id;
    const file = inputElement.files[0];

    if (!file) {
        alert("No file selected.");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);
    formData.append("donation_id", donationId);
    // http://127.0.0.1:8000/upload-donation-image/ 
    fetch(`/donor_dashboard/upload-donation-image/`, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": getCsrfToken(), // Include CSRF token
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Image uploaded successfully!");
                // Update the image src to the new image URL
                location.reload();
            } else {
                alert("Failed to upload image. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error uploading image:", error);
            alert("An error occurred while uploading the image.");
        });
}

// Get CSRF token from the DOM (assumes Django template includes CSRF token)
function getCsrfToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
}


document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("contribute-modal");
    const openModalBtns = document.querySelectorAll(".open-modal");
    const closeModalBtns = document.querySelectorAll(".close-btn");
    const contributeForm = document.getElementById("contribute-form");
    const contributionsTable = document.getElementById("contributions");
    const orgDropdown = document.getElementById("donor_organization");
    const mealsInput = document.getElementById("meals");
    const volunteersInput = document.getElementById("volunteers");
    const donorOrganizationDropdown = document.getElementById("donor_organization");
    const deleteBtn = document.getElementById("delete-btn"); // Assuming you have a delete button
    const modalHeader = modal.querySelector(".modal-card-head");

    // Open modal when button is clicked
    openModalBtns.forEach(btn =>
        btn.addEventListener("click", () => {
            const target = document.getElementById(btn.dataset.target);
            // Ensure the modal header is visible
            if (modalHeader) {
                modalHeader.style.display = ""; // Reset display property
            }
            // Initially hide the delete button
            deleteBtn.hidden = true;

            // Clear the dropdown selection
            if (donorOrganizationDropdown) {
                donorOrganizationDropdown.selectedIndex = 0; // Reset to the first option
            }
            mealsInput.value = "";
            volunteersInput.value = "";
            modal.classList.add("is-active");
        })
    );

    // Close modal when button is clicked
    closeModalBtns.forEach(btn =>
        btn.addEventListener("click", () => {
            modal.classList.remove("is-active");
        })
    );

    // Fetch participation details dynamically when dropdown changes
    orgDropdown.addEventListener("change", () => {
        const selectedOrgId = orgDropdown.value;
        mealsInput.value = "";
        volunteersInput.value = "";
    
        // Initially hide the delete button
        deleteBtn.hidden = true;
    
        // Make AJAX request to fetch participation details
        fetch(`/community_drives/participation-details/${selectedOrgId}/${driveId}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                // Populate the modal fields with fetched data
                mealsInput.value = data.meals || 0; // Default to 0 if no data
                volunteersInput.value = data.volunteers || 0; // Default to 0 if no data
    
                // Show the delete button if there is a previous contribution
                if (data.meals > 0 || data.volunteers > 0) {
                    deleteBtn.hidden = false;
                } else {
                    deleteBtn.hidden = true;
                }
            })
            .catch(error => {
                console.error("Error fetching participation details:", error);
                mealsInput.value = 0; // Reset to empty if an error occurs
                volunteersInput.value = 0; // Reset to empty if an error occurs
                deleteBtn.hidden = true; // Ensure the delete button stays hidden on error
            });
    });

    fetch(`/community_drives/fetch-contributions/${driveId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            updateContributions(data);
        })
        .catch(error => {
            console.error("Error fetching contributions:", error);
        });
        

    // Handle form submission
    contributeForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent normal form submission
        const meals = mealsInput.value;
        const volunteers = volunteersInput.value;
        const donorOrganization = orgDropdown.value;

        // Send data via AJAX (using Fetch API)
        fetch(`/community_drives/drives/${driveId}/contribute/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify({
                meals: meals,
                volunteers: volunteers,
                donor_organization: donorOrganization
            })
        })
            .then(response => response.json())
            .then(data => {
                // Close the modal and show success message
                modal.classList.remove("is-active");
                mealsInput.value = "";
                volunteersInput.value = "";
                if (data.success) {
                    contributionsTable.replaceChildren();
                    contributionsTable.innerHTML = "";
                    // Populate the table with the updated contributions
                    updateContributions(data);
                    alert("Thank you for your contribution!");
                } else {
                    alert("Failed to contribute." + data.error);
                }
            })
            .catch(error => {
                // Close the modal and reset fields
                modal.classList.remove("is-active");
                mealsInput.value = "";
                volunteersInput.value = "";
                alert("There was an error submitting your contribution." + error.message);
            });
    });

    // Handle delete participation (ensure it doesn't trigger form submission)
    deleteBtn.addEventListener("click", (event) => {
        event.preventDefault(); // Prevent form submission if delete button is clicked
        const selectedOrgId = orgDropdown.value;

        // Make AJAX request to delete participation
        fetch(`/community_drives/delete_participation/${selectedOrgId}/${driveId}/`, {
            method: "DELETE",
            headers: {
                "X-CSRFToken": document.querySelector('[name="csrfmiddlewaretoken"]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                modal.classList.remove("is-active");
                // Update the table or reset fields accordingly
                contributionsTable.innerHTML = "";
                updateContributions(data);
                alert("Contribution successfully deleted!");
            } else {
                alert("Failed to delete contribution: " + data.error);
            }
        })
        .catch(error => {
            console.error("Error deleting contribution:", error);
            alert("There was an error deleting the contribution.");
        });
    });
});


function updateContributions(data) {
    const contributionsTable = document.getElementById("contributions");
    data.contributions.forEach(contribution => {
        const row = document.createElement("article");
        row.className = 'media is-align-items-center';
        const iconContainer = document.createElement('figure');
        iconContainer.className = 'media-left';
        iconContainer.innerHTML = `
            <span class="icon is-medium has-text-primary">
                <span class="fa-stack fa-sm">
                    <i class="fa fa-circle fa-stack-2x"></i>
                    <i class="fa fa-heart fa-stack-1x fa-inverse"></i>
                </span>
            </span>
        `;
        row.appendChild(iconContainer);

        const cardContainer = document.createElement('div');
        cardContainer.className = 'media-content';
        const formattedDate = new Date(contribution.created_at).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          });
        cardContainer.innerHTML = `
            <div class="card">
            <div class="card-content">
                <div class="columns is-vcentered">
                <div class="column is-half">
                    <p>
                    <strong><span class="has-text-primary">${contribution.organization_name}</span></strong> contributed
                    <br />
                    <small>${formattedDate}</small>
                    </p>
                </div>
                <div class="column has-text-centered">
                    <p>
                    <span class="tag is-success is-medium">${contribution.meals_contributed}</span>
                    <br />
                    <small>meals</small>
                    </p>
                </div>
                <div class="column has-text-centered">
                    <p>
                    <span class="tag is-info is-medium">${contribution.volunteers_contributed}</span>
                    <br />
                    <small>volunteers</small>
                    </p>
                </div>
            </div>
            </div>
            </div>
        `;
        row.appendChild(cardContainer);
        contributionsTable.appendChild(row);
    });
}


function uploadDriveImage(inputElement) {
    const driveId = inputElement.dataset.id;
    const file = inputElement.files[0];

    if (!file) {
        alert("No file selected.");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);
    formData.append("drive_id", driveId);
    // http://127.0.0.1:8000/upload-donation-image/ 
    fetch(`/community_drives/upload-drive-image/`, {
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

function deleteDriveImage(inputElement) {
    const driveId = inputElement.dataset.id;
    if (confirm('Are you sure you want to delete this donation image?')) {

        const formData = new FormData();
        formData.append("drive_id", driveId);
        // http://127.0.0.1:8000/delete-donation-image/ 
        fetch(`/community_drives/delete-drive-image/`, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCsrfToken(), // Include CSRF token
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Image deleted successfully!");
                    // Update the image src to the new image URL
                    location.reload();
                } else {
                    alert("Failed to delete image. Please try again.");
                }
            })
            .catch(error => {
                console.error("Error deleting image:", error);
                alert("An error occurred while deleting the image.");
            });
    }
}

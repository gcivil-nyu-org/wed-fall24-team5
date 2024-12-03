document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("contribute-modal");
    const openModalBtns = document.querySelectorAll(".open-modal");
    const closeModalBtns = document.querySelectorAll(".close-btn");
    const contributeForm = document.getElementById("contribute-form");
    const contributionsTable = document.getElementById("contributions-table");

    openModalBtns.forEach(btn =>
        btn.addEventListener("click", () => {
            const target = document.getElementById(btn.dataset.target);
            target.classList.add("is-active");
        })
    );

    closeModalBtns.forEach(btn =>
        btn.addEventListener("click", () => {
            modal.classList.remove("is-active");
        })
    );

    contributeForm.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent normal form submission
        const meals = document.getElementById("meals").value;
        const volunteers = document.getElementById("volunteers").value;
        const donorOrganization = document.getElementById("donor_organization").value;
        const driveId = contributeForm.dataset.driveId;

        // Send data via AJAX (using Fetch API)
        fetch(`/community_drives/drives/${driveId}/contribute/`, {  // Use the dynamic URL with drive_id
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
            document.getElementById("meals").value = "";
            document.getElementById("volunteers").value = "";
            if (data.success) {
                contributionsTable.innerHTML = "";

                // Populate the table with the updated contributions
                data.contributions.forEach(contribution => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${contribution.organization_name}</td>
                        <td>${contribution.meals_contributed}</td>
                        <td>${contribution.volunteers_contributed}</td>
                    `;
                    contributionsTable.appendChild(row);
                });

                alert("Thank you for your contribution!");
            } else {
                alert("Failed to contribute." + data.error);
            }
        })
        .catch(error => {
            // Close the modal and show success message
            modal.classList.remove("is-active");
            document.getElementById("meals").value = "";
            document.getElementById("volunteers").value = "";
            alert("There was an error submitting your contribution." + error.error);
        });
        
    });
});


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
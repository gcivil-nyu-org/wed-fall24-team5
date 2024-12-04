document.addEventListener('DOMContentLoaded', () => {
    // Tab switching functionality and remember what tab we are on by using localStorage
    const tabs = document.querySelectorAll('.tabs ul li');
    const driveLists = document.querySelectorAll('.drive-list');

    // Get the active tab from localStorage or default to 'pending-tab'
    const savedTab = localStorage.getItem('activeTab') || 'all-drives-tab';

    // Check if the savedTab matches any tab, otherwise default to 'pending-tab'
    let activeTabExists = false;
    tabs.forEach((tab, index) => {
        if (tab.id === savedTab) {
            tab.classList.add('is-active');
            driveLists[index].classList.remove('is-hidden');
            activeTabExists = true;
        } else {
            tab.classList.remove('is-active');
            driveLists[index].classList.add('is-hidden');
        }
    });

    // If no matching tab was found, set 'pending-tab' as the default active tab and show its content
    if (!activeTabExists) {
        const defaultTab = document.getElementById('all-drives-tab');
        const defaultContent = document.getElementById('all-drives');

        if (defaultTab && defaultContent) {
            defaultTab.classList.add('is-active');
            defaultContent.classList.remove('is-hidden');
        }
    }

    // Add click event listeners to tabs
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and hide all order lists
            tabs.forEach(t => t.classList.remove('is-active'));
            driveLists.forEach(list => list.classList.add('is-hidden'));

            // Activate the selected tab and show the corresponding content
            tab.classList.add('is-active');
            driveLists[index].classList.remove('is-hidden');

            // Save the selected tab in localStorage
            localStorage.setItem('activeTab', tab.id);
        });
    });

    function openModal($el) {
        $el.classList.add('is-active');
    }

    function closeModal($el) {
        $el.classList.remove('is-active');
    }

    function closeAllModals() {
        (document.querySelectorAll('.modal') || []).forEach(($modal) => {
            closeModal($modal);
        });
    }

    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.open-modal') || []).forEach(($trigger) => {
        const modal = $trigger.dataset.target;
        const $target = document.getElementById(modal);

        $trigger.addEventListener('click', () => {
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .is-delete, .close-btn') || []).forEach(($close) => {
        const $target = $close.closest('.modal');

        $close.addEventListener('click', () => {
            closeModal($target);
        });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeAllModals();
        }
    });

    // Frontend form validation warnings
    const submitButton = document.querySelector('button[type="submit"]');

    const nameInput = document.getElementById("id_name");
    const nameWarning = document.getElementById("name-warning");
    nameInput.addEventListener("input", function () {
        const nameValue = nameInput.value;
        if (nameValue.length > 250) {
            nameWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            nameWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    const descriptionInput = document.getElementById("id_description");
    const descriptionWarning = document.getElementById("description-warning");
    descriptionInput.addEventListener("input", function () {
        const descriptionValue = descriptionInput.value;
        if (descriptionValue.length > 1000) {
            descriptionWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            descriptionWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    const targetInput = document.getElementById("id_meal_target");
    const targetWarning = document.getElementById("target-warning");
    targetInput.addEventListener("input", function () {
        const targetValue = targetInput.value;
        if (targetValue && targetValue <= 0) {
            targetWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            targetWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    const volunteerInput = document.getElementById("id_volunteer_target");
    const volunteerWarning = document.getElementById("volunteer-warning");
    volunteerInput.addEventListener("input", function () {
        const volunteerValue = volunteerInput.value;
        if (volunteerValue && volunteerValue <= 0) {
            volunteerWarning.style.display = "block";
            submitButton.setAttribute("disabled", "true");
            submitButton.classList.add("is-disabled");
        } else {
            volunteerWarning.style.display = "none";
            submitButton.removeAttribute("disabled");
            submitButton.classList.remove("is-disabled");
        }
    });

    const startDateInput = document.getElementById("id_start_date");
    const endDateInput = document.getElementById("id_end_date");
    const dateWarning = document.getElementById("date-warning");

    function validateDates() {
        const startDateValue = new Date(startDateInput.value);
        const endDateValue = new Date(endDateInput.value);
        const today = new Date();

        // Clear the error message if either field is empty
        if (!startDateInput.value || !endDateInput.value) {
            dateWarning.textContent = "";
            dateWarning.style.display = "none";
            return;
        }

        // Check if both dates are in the future
        if (startDateValue <= today || endDateValue <= today) {
            dateWarning.textContent = "Date must not be in the past.";
            dateWarning.style.display = "block";
            return;
        }

        // Check if end date is after the start date
        if (startDateValue > endDateValue) {
            dateWarning.textContent = "Start date must be before the end date.";
            dateWarning.style.display = "block";
            return;
        }

        // Clear error message if all validations pass
        dateWarning.textContent = "";
        dateWarning.style.display = "none";
    }

    startDateInput.addEventListener("input", validateDates());
    endDateInput.addEventListener("input", validateDates());

    document.querySelectorAll('.short-text').forEach(element => {
        const maxChars = 300;
        if (element.textContent.length > maxChars) {
            element.textContent = element.textContent.slice(0, maxChars - 3) + ' ...';
        }
    });
});


// document.addEventListener("DOMContentLoaded", () => {
//     const images = document.querySelectorAll(".image.is-clickable");
//     images.forEach(image => {
//         image.addEventListener("click", () => {
//             const donationId = image.getAttribute("data-donation-id");
//             triggerFileUpload(donationId);
//         });
//     });
// });


// function triggerFileUpload(donationId) {
//     document.getElementById(`file-upload-${donationId}`).click();
// }

function confirmDeleteDrive(driveId) {
    if (confirm('Are you sure you want to delete this drive?')) {
        document.getElementById('delete-form-' + driveId).submit();
    }
}

// Handle file upload and send to the server
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
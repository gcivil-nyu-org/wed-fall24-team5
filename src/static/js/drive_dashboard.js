document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("contribute-modal");
    const openModalBtns = document.querySelectorAll(".open-modal");
    const closeModalBtns = document.querySelectorAll(".close-btn");
    const contributeForm = document.getElementById("contribute-form");
    const contributionsTable = document.getElementById("contributions-table");
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
        const driveId = contributeForm.dataset.driveId;
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
        

    // Handle form submission
    contributeForm.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent normal form submission
        const meals = mealsInput.value;
        const volunteers = volunteersInput.value;
        const donorOrganization = orgDropdown.value;
        const driveId = contributeForm.dataset.driveId;

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
                    contributionsTable.innerHTML = "";

                    // Populate the table with the updated contributions
                    data.contributions.forEach(contribution => {
                        const row = document.createElement("tr");
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
        const driveId = contributeForm.dataset.driveId;

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
                // Update the table or reset fields accordingly
                contributionsTable.innerHTML = "";

                    // Populate the table with the updated contributions
                    data.contributions.forEach(contribution => {
                        const row = document.createElement("tr");
                        row.innerHTML = `
                            <td>${contribution.organization_name}</td>
                            <td>${contribution.meals_contributed}</td>
                            <td>${contribution.volunteers_contributed}</td>
                        `;
                        contributionsTable.appendChild(row);
                    });
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

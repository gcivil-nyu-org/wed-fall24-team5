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

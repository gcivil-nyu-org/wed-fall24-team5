document.addEventListener('DOMContentLoaded', function () {
    async function handleFormSubmit(event) {
        const form = document.getElementById("addAdminForm");
        const url = form.getAttribute("data-check-url");
        event.preventDefault(); // Prevent the default form submission

        const email = document.getElementById("email").value;
        const confirmButton = document.getElementById("confirmButton");

        // Check if the email exists by making a request to the server
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.exists) {
            // If user exists, submit the form
            document.getElementById("addAdminForm").submit();
        } else {
            // Show confirmation message and button if user doesn't exist
            document.getElementById("addAdminModal").classList.add("is-active");
        }
    }

    function confirmAddUser() {
        closeModal();
        document.getElementById("addAdminForm").submit(); // Submit the form after confirmation
    }

    // Functions to open and close a modal
    function openModal($el) {
        $el.classList.add('is-active');
    }

    function closeModal() {
        document.getElementById('addAdminModal').classList.remove('is-active');
    }

    // Add a click event on buttons to open a specific modal
    (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {
        const modal = $trigger.dataset.target;
        const $target = document.getElementById(modal);

        $trigger.addEventListener('click', () => {
            openModal($target);
        });
    });

    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .delete, .button') || []).forEach(($close) => {
        $close.addEventListener('click', () => {
            closeModal();
        });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
        if (event.key === "Escape") {
            closeModal();
        }
    });

    document.getElementById("addAdminForm").addEventListener("submit", handleFormSubmit);
    document.querySelector('.button.is-primary').addEventListener('click', confirmAddUser);
});
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('reviewModal');
    const reviewButtons = document.querySelectorAll('.review-btn');
    const closeModalBtn = modal.querySelector('.delete');
    const cancelBtn = document.getElementById('closeModal');
    const submitBtn = document.getElementById('submitReview');
    const orderIdInput = document.getElementById('orderId');
    const ratingInput = document.getElementById('ratingInput');
    const commentInput = document.getElementById('comment');
    const stars = document.querySelectorAll('#starRating i');
    let selectedRating = 0;

    // Function to open modal and populate fields if review exists
    function openModal(orderId, existingRating, existingComment) {
        orderIdInput.value = orderId;
        modal.classList.add('is-active');

        // If a rating exists, populate the modal with the existing rating
        if (existingRating && existingRating !== '0') {
            selectedRating = existingRating;
            ratingInput.value = existingRating;
            updateStars(existingRating); // Update the stars based on the existing rating
        } else {
            resetStars(); // Reset stars if no existing rating
        }

        // Set the comment if it exists
        if (existingComment) {
            commentInput.value = existingComment;
        } else {
            commentInput.value = ''; // Clear the comment field if no comment exists
        }
    }

    function resetModal() {
        selectedRating = 0;
        resetStars();
        ratingInput.value = '';
        commentInput.value = '';
    }

    // Modify your closeModal function to reset the modal
    function closeModal() {
        resetModal();
        modal.classList.remove('is-active');
    }

    // Reset stars to default (empty stars)
    function resetStars() {
        selectedRating = 0;
        updateStars(selectedRating);
        ratingInput.value = ''; // Clear the hidden input
    }

    // Update stars based on rating value
    function updateStars(rating) {
        stars.forEach((star) => {
            if (star.getAttribute('data-value') <= rating) {
                star.classList.remove('fa-star-o');
                star.classList.add('fa-star', 'selected');
            } else {
                star.classList.remove('fa-star', 'selected');
                star.classList.add('fa-star-o');
            }
        });
    }

    // Event listeners for star rating system
    stars.forEach((star) => {
        star.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            selectedRating = value;
            ratingInput.value = value; // Set hidden input with the selected rating
            updateStars(value);
        });

        star.addEventListener('mouseover', function () {
            const value = this.getAttribute('data-value');
            updateStars(value); // Provide hover feedback
        });

        star.addEventListener('mouseout', function () {
            updateStars(selectedRating); // Reset stars to selected rating after hover
        });
    });

    // Event listeners for open and close modal
    reviewButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const orderId = event.target.getAttribute('data-order-id');
            const existingRating = event.target.getAttribute('data-rating');
            const existingComment = event.target.getAttribute('data-comment');

            openModal(orderId, existingRating, existingComment);
        });
    });

    closeModalBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Submit review
    submitBtn.addEventListener('click', () => {
        document.getElementById('reviewForm').submit();
    });
});

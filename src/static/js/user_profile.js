function toggleSelection(button, name) {
    const hiddenInput = document.getElementById(name);
    const isSelected = button.classList.contains('is-success');

    button.classList.toggle('is-success', !isSelected);

    // Update hidden input based on selection
    hiddenInput.value = !isSelected;
}
document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('advanced-options-btn');
    button.addEventListener('click', function() {
        const advancedOptions = document.getElementById('advanced-options');
        if (advancedOptions.classList.contains('is-hidden')) {
            advancedOptions.classList.remove('is-hidden');
        } else {
            advancedOptions.classList.add('is-hidden');
        }
    });
});

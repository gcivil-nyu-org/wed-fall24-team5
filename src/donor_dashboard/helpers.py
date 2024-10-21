from django.utils import timezone


def validate_donation(food_item, quantity, pickup_by, organization_id):
    errors = []

    # Validate food_item such that it is not empty
    if not food_item:
        errors.append("Food item cannot be empty.")

    # Validate quantity such that it is equal to greater than 0
    if not quantity.isdigit() or int(quantity) < 0:
        errors.append("Quantity must be a positive integer.")

    # Validate pickup_by date such that the date is between today and one week from today.
    try:
        pickup_date = timezone.datetime.strptime(pickup_by, "%Y-%m-%d").date()
        today = timezone.now().date()
        one_week_later = today + timezone.timedelta(weeks=1)

        if not (today <= pickup_date <= one_week_later):
            errors.append("Pickup date must be between today and one week from today.")
    except ValueError:
        errors.append("Invalid date format. Please use YYYY-MM-DD.")

    # Validate organization_id
    if not organization_id:
        errors.append("Organization ID is required.")

    return errors

from django import forms
from database.models import Donation
from django.utils import timezone


class AddDonationForm(forms.ModelForm):
    food_item = forms.CharField(
        required=True,
        label="Food Item",
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "type": "text",
                "placeholder": "Food Item",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    quantity = forms.IntegerField(
        required=True,
        label="Quantity",
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "Quantity",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    pickup_by = forms.DateField(
        required=True,
        label="Pickup Date",
        widget=forms.DateInput(
            attrs={
                "class": "input",
                "type": "date",
                "placeholder": "Select date",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    class Meta:
        model = Donation
        fields = [
            "food_item",
            "quantity",
            "pickup_by",
        ]

    def clean(self):
        cleaned_data = super().clean()
        food_item = cleaned_data.get("food_item")
        quantity = cleaned_data.get("quantity")
        pickup_by = cleaned_data.get("pickup_by")

        if food_item is None:
            raise forms.ValidationError("Food item is required.")

        if quantity is None or quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive integer.")

        try:
            today = timezone.now().date()
            one_week_later = today + timezone.timedelta(weeks=1)
            if not (today <= pickup_by <= one_week_later):
                raise forms.ValidationError(
                    "Pickup date must be between today and one week from today."
                )
        except ValueError:
            raise forms.ValidationError("Invalid date format. Please use YYYY-MM-DD.")

        return cleaned_data

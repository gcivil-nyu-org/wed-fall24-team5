from django import forms
from database.models import Organization


class SearchDonationForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Search for a donation",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 0px 6px 6px 0px;
            """,
            }
        ),
    )

    type = forms.ChoiceField(
        required=False,
        label="Filter by",
        choices=[("", "Filter by all"), ("food", "Food item"), ("org", "Organization")],
        widget=forms.Select(
            attrs={
                "class": "is-primary",
                "style": """
                border: none;
                background-color: #EDEAF5;
                border-radius: 6px 0px 0px 6px;
                height: auto;
                box-shadow: none;
                padding-right: 2em;
                padding-left: 1em;
            """,
            }
        ),
    )

    category = forms.ChoiceField(
        required=False,
        label="Organization Type",
        choices=[("", "Category")] + Organization.ORGANIZATION_TYPES,
        widget=forms.Select(
            attrs={
                "class": "select is-fullwidth",
                "style": """
                border: none;
                background-color: #EDEAF5;
                border-radius: 6px;
                height: auto;
                padding: 0.5em;
                box-shadow: none;
                padding-right: 2em;
                padding-left: 1em;
            """,
            }
        ),
    )

    date = forms.DateField(
        required=False,
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

    min_quantity = forms.IntegerField(
        required=False,
        label="Quantity Available",
        min_value=1,  # This enforces minimum value of 1
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "1",  # Updated placeholder to reflect minimum value
                "min": "1",  # HTML5 validation for number input
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            },
        ),
    )

    address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "placeholder": "Enter address or location",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
                "id": "location-input",
            }
        ),
    )

    radius = forms.ChoiceField(
        required=False,
        label="Search Radius",
        initial=0.5,  # Set default value
        choices=[
            ("0.5", "0.5 miles"),  # Change to strings for better form handling
            ("1", "1 mile"),
            ("3", "3 miles"),
            ("5", "5 miles"),
            ("10", "10 miles"),
        ],
        widget=forms.Select(
            attrs={
                "class": "select",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
                """,
            }
        ),
    )

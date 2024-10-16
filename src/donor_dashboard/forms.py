from django import forms
from database.models import Organization

INPUT_CLASS = "input"


class AddOrganizationForm(forms.ModelForm):
    organization_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": f"{INPUT_CLASS}",
                "type": "text",
                "placeholder": "Organization name",
                "style": "background-color: transparent; border-radius: 6px;",
            }
        ),
        error_messages={"required": "Organization name is required."},
    )

    type = forms.ChoiceField(
        required=True,
        choices=[("", "Organization Type...")] + Organization.ORGANIZATION_TYPES,
        widget=forms.Select(
            attrs={
                "class": "is-primary is-light is-medium",
                "style": """
                border: none;
                background-color: transparent;
                border-radius: 6px;
                height: auto;
                padding: 0.5em;
                box-shadow: none;
                outline: none;
                padding-right: 2em;
            """,
            }
        ),
        error_messages={"required": "Please select the organization type."},
    )

    address = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "button is-link is-light is-fullwidth has-text-left is-flex-wrap-wrap",
                "type": "text",
                "placeholder": "Address",
                "style": """
                border: none;
                background-color:
                transparent;
                border-radius: 6px;
                box-shadow: none;
                outline: none;""",
            }
        ),
        error_messages={"required": "Address is required."},
    )

    zipcode = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": f"{INPUT_CLASS} mt-2",
                "type": "number",
                "placeholder": "Zipcode",
                "style": "background-color: transparent; border-radius: 6px;",
            }
        ),
        error_messages={"required": "Zipcode is required."},
    )

    contact_number = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": f"{INPUT_CLASS}",
                "type": "tel",
                "placeholder": "Phone number",
                "style": "background-color: transparent; border-radius: 6px;",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": f"{INPUT_CLASS}",
                "type": "email",
                "placeholder": "Email",
                "style": "background-color: transparent; border-radius: 6px;",
            }
        ),
        error_messages={"required": "Email is required."},
    )

    website = forms.URLField(
        required=True,
        widget=forms.URLInput(
            attrs={
                "class": f"{INPUT_CLASS}",
                "type": "url",
                "placeholder": "Website URL",
                "style": "background-color: transparent; border-radius: 6px;",
            }
        ),
    )

    class Meta:
        model = Organization
        fields = [
            "organization_name",
            "type",
            "address",
            "zipcode",
            "contact_number",
            "email",
            "website",
        ]

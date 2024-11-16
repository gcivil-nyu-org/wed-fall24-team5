import re
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

    def clean_organization_name(self):
        organization_name = self.cleaned_data.get("organization_name")
        print(f"Validating organization_name: {organization_name}")
        if len(organization_name) < 3:
            print("error")
            raise forms.ValidationError(
                "Organization name should be at least 3 characters."
            )
        return organization_name

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

    def clean_address(self):
        address = self.cleaned_data.get("address")
        if len(address) < 5:
            raise forms.ValidationError("Address should be at least 5 characters.")
        return address

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

    def clean_zipcode(self):
        zipcode = self.cleaned_data.get("zipcode")
        if len(str(zipcode)) != 5 or not str(zipcode).isdigit():
            raise forms.ValidationError("Enter a valid zipcode.")
        return zipcode

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

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get("contact_number")
        contact_number_regex = r"^\+?1?\d{9,15}$"
        if not re.match(contact_number_regex, contact_number):
            raise forms.ValidationError("Enter a valid phone number.")
        return contact_number

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

    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            raise forms.ValidationError("Enter a valid email address.")
        return email

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

    def clean_website(self):
        website = self.cleaned_data.get("website")
        website_regex = r"^(http|https)://"
        if not re.match(website_regex, website):
            raise forms.ValidationError("Enter a valid website URL.")
        return website

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

from django import forms
from database.models import CommunityDrive, Organization
from django.utils import timezone


class AddCommunityDriveForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        label="Name",
        widget=forms.TextInput(
            attrs={
                "class": "input",
                "type": "text",
                "placeholder": "Name of your community drive",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    description = forms.CharField(
        required=True,
        label="Description",
        widget=forms.Textarea(
            attrs={
                "class": "input",
                "type": "text",
                "placeholder": "Brief description (max 1000 characters)",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    lead_organization = forms.ModelChoiceField(
        required=True,
        label="Lead Organization",
        queryset=Organization.objects.none(),
        empty_label="Start drive as...",
        widget=forms.Select(
            attrs={
                "class": "input",
                "type": "date",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    meal_target = forms.IntegerField(
        required=True,
        label="Meal Target",
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "0",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    volunteer_target = forms.IntegerField(
        required=False,
        label="Volunteer Target",
        widget=forms.NumberInput(
            attrs={
                "class": "input",
                "placeholder": "0",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    start_date = forms.DateField(
        required=True,
        label="Start Date",
        widget=forms.DateInput(
            attrs={
                "class": "input",
                "type": "date",
                "placeholder": "Select start date",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    end_date = forms.DateField(
        required=True,
        label="End Date",
        widget=forms.DateInput(
            attrs={
                "class": "input",
                "type": "date",
                "placeholder": "Select end date",
                "style": """
                background-color: transparent;
                border-color: #CCC;
                border-radius: 6px;
            """,
            }
        ),
    )

    class Meta:
        model = CommunityDrive
        fields = [
            "name",
            "description",
            "lead_organization",
            "meal_target",
            "volunteer_target",
            "start_date",
            "end_date",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None:
            # Get user's organizations to populate lead organization field
            self.fields["lead_organization"].queryset = Organization.objects.filter(
                organizationadmin__user=user
            )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        description = cleaned_data.get("description")
        meal_target = cleaned_data.get("meal_target")
        volunteer_target = cleaned_data.get("volunteer_target")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if name is None or len(name) > 250:
            raise forms.ValidationError(
                "Please enter a name between 1 and 250 characters."
            )

        if description is None or len(description) > 1000:
            raise forms.ValidationError(
                "Please enter a name between 1 and 1000 characters."
            )

        if meal_target <= 0 or volunteer_target < 0:
            raise forms.ValidationError("Target numbers must be positive integers.")

        try:
            today = timezone.now().date()
            if start_date and end_date:
                if start_date < today or end_date < today:
                    raise forms.ValidationError("Date cannot be in the past.")
                if end_date < start_date:
                    raise forms.ValidationError("Start date must be before end date.")
        except ValueError:
            raise forms.ValidationError("Invalid date format. Please use YYYY-MM-DD.")

        return cleaned_data

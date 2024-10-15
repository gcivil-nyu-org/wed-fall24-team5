from django import forms
from database.models import Organization

class AddOrganizationForm(forms.ModelForm):
	# organization_name = forms.CharField(
    #     required=True,
    #     widget=forms.TextInput(
    #         attrs={
    #             "type": "text",
    #         }
    #     ),
    #     error_messages={"required": "Name is required."},
    # )
	# type = forms.ChoiceField(
    #     required=True,
    #     widget=forms.TextInput(
    #         attrs={
    #             "class": INPUT_CLASS,
    #             "type": "text",
    #         }
    #     ),
    #     error_messages={"required": "Name is required."},
    # )
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
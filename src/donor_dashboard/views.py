from django.shortcuts import render, redirect  # noqa
from database.models import Organization, OrganizationAdmin, User
from django.contrib import messages
from .forms import AddOrganizationForm
from django.contrib.auth.decorators import login_required

@login_required
def add_organization(request):
	if request.method == 'POST':
		form = AddOrganizationForm(request.POST)
		if form.is_valid():
			organization = form.save()
			org_user = User.objects.get(user_email=request.user.email)
			OrganizationAdmin.objects.create(
				user_email=org_user,
				organization_id=organization
				)
			messages.success(
                request, "Organization successfully added."
            )
			return redirect("/")
	else:
		form = AddOrganizationForm()
	return render(request, "add_organization.html", {"form": form})

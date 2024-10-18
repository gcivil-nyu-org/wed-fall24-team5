from database.models import OrganizationAdmin, User, Organization


def user_organizations(request):
    if request.user.is_authenticated:
        # Get all organizations the logged-in user belongs to
        org_user = User.objects.get(email=request.user.email)
        # org_admins = OrganizationAdmin.objects.filter(user=org_user)
        # organizations = [org_admin.organization for org_admin in org_admins]
        organizations = Organization.objects.filter(organizationadmin__user=org_user.id);
    else:
        organizations = []

    return {"user_organizations": organizations}

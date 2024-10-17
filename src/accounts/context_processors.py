from database.models import OrganizationAdmin, User


def user_organizations(request):
    if request.user.is_authenticated:
        # Get all organizations the logged-in user belongs to
        org_user = User.objects.get(email=request.user.email)
        org_admins = OrganizationAdmin.objects.filter(user=org_user)
        organizations = [org_admin.organization_id for org_admin in org_admins]
    else:
        organizations = []

    return {"user_organizations": organizations}

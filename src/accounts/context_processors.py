from database.models import OrganizationAdmin

def user_organizations(request):
    if request.user.is_authenticated:
        # Get all organizations the logged-in user belongs to
        org_admins = OrganizationAdmin.objects.filter(user_email=request.user.email)
        organizations = [org_admin.organization_id for org_admin in org_admins]
    else:
        organizations = []

    return {
        "user_organizations": organizations
    }
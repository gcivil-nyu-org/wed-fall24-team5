from database.models import User, Organization

def user_organizations(request):
    if request.user.is_authenticated:
        # Get all organizations the logged-in user belongs to
        org_user = User.objects.get(email=request.user.email)
        organizations = Organization.objects.filter(organizationadmin__admin_id=org_user.id)
    else:
        organizations = []

    return {"user_organizations": organizations}

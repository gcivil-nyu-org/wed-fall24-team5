from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from database.models import DietaryRestriction, UserProfile
from django.contrib import messages
from django.db import transaction


@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    # Fetch the existing restrictions for the user
    existing_restrictions = DietaryRestriction.objects.filter(user=request.user)
    user_restrictions = [restriction.restriction.lower().replace(" ", "_") for restriction in existing_restrictions]
    custom_restriction = next((r.restriction for r in existing_restrictions if r.restriction not in user_restrictions), "")

    # default dietary restrictions
    default_restrictions = [
        {"name": "gluten_free", "label": "Gluten Free"},
        {"name": "dairy_free", "label": "Dairy Free"},
        {"name": "no_nuts", "label": "No Nuts"},
        {"name": "no_shellfish", "label": "No Shellfish"},
        {"name": "vegetarian", "label": "Vegetarian"},
        {"name": "vegan", "label": "Vegan"},
    ]

    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            phone_number = request.POST.get("phone_number")

            custom_restriction = request.POST.get("custom_restriction")
            
            with transaction.atomic():  # Begin a new atomic transaction block
                user_profile.user.first_name = first_name
                user_profile.user.last_name = last_name
                user_profile.user.save()
                user_profile.phone_number = phone_number
                user_profile.save()

                # Clear existing dietary restrictions
                DietaryRestriction.objects.filter(user=request.user).delete()

                # Add new dietary restrictions based on form values
                for restriction in default_restrictions:
                    print(restriction['name'])
                    if request.POST.get(restriction['name']) == "true":
                        print("hit true")
                        DietaryRestriction.objects.create(
                            user=request.user, restriction=restriction['name']
                        )

                # Handle custom restriction
                if custom_restriction:
                    DietaryRestriction.objects.create(
                        user=request.user, restriction=custom_restriction
                    )
            messages.success(request, "Profile updated successfully!")
        except:  # noqa
            messages.warning(request, "Some error occured while updating your profile!")
        return redirect("user_profile:profile")

    return render(request, "user_profile/profile.html", {
        "user_profile": user_profile,
        "user_restrictions": user_restrictions,
        "custom_restriction": custom_restriction,
        "dietary_restrictions": default_restrictions
    })

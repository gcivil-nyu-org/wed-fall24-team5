from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from database.models import UserProfile
from django.contrib import messages
from django.db import transaction


@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            phone_number = request.POST.get("phone_number")

            with transaction.atomic():  # Begin a new atomic transaction block
                user_profile.user.first_name = first_name
                user_profile.user.last_name = last_name
                user_profile.user.save()
                user_profile.phone_number = phone_number
                user_profile.save()

            messages.success(request, "Profile updated successfully!")
        except: # noqa
            messages.warning(request, "Some error occured while updating your profile!")
        return redirect("user_profile:profile")

    return render(request, "user_profile/profile.html", {"user_profile": user_profile})

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from database.models import Room, Organization
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

@login_required
def messaging_view(request):
    user_id = request.user.id
    organizations = Organization.objects.all()
    rooms = Room.objects.filter(Q(conversor_1_id=user_id) | Q(conversor_2_id=user_id))
    return render(
        request,
        "messaging_dashboard.html",
        {"organizations": organizations, "rooms": rooms},
    )

@login_required
def start_conversation(request):
    if request.method == "POST":
        sender_id = request.POST["sender_id"]
        receiver_id = request.POST["receiver_id"]
        sender_type = request.POST["sender_type"]
        receiver_type = request.POST["receiver_type"]

        if sender_type == "user" and receiver_type == "organization":
            sender = User.objects.get(id=sender_id)
            receiver = Organization.objects.get(organization_id=receiver_id)
            room_id = f"{sender_id}_{receiver_id}"
            room_name = f"Chat with {sender.first_name} and {receiver}"
            conversor_1_type = ContentType.objects.get_for_model(sender)
            conversor_1_id = sender.id
            conversor_2_type = ContentType.objects.get_for_model(receiver)
            conversor_2_id = (receiver.organization_id,)

        elif sender_type == "organization" and receiver_type == "user":
            sender = User.objects.get(id=sender_id)
            receiver = Organization.objects.get(organization_id=receiver_id)
            room_id = f"{receiver_id}_{sender_id}"
            room_name = f"Chat with {receiver.first_name} and {sender}"
            conversor_1_type = ContentType.objects.get_for_model(sender)
            conversor_1_id = sender.organization_id
            conversor_2_type = ContentType.objects.get_for_model(receiver)
            conversor_2_id = receiver.id

        try:
            room = Room.objects.get(room_id=room_id)
            messages.warning(request, f"Chat already exists with {receiver}")
        except ObjectDoesNotExist:
            room = Room(
                room_id=room_id,
                room_name=room_name,
                conversor_1_type=conversor_1_type,
                conversor_1_id=conversor_1_id,
                conversor_2_type=conversor_2_type,
                conversor_2_id=conversor_2_id,
            )
            room.save()
            messages.success(request, f"Created a new chat with {receiver}")

        return redirect("messaging:messaging")  
    return redirect("messaging:messaging")



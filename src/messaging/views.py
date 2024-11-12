from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from database.models import Room, Organization, Message
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


def get_rooms(id):
    filtered_rooms = Room.objects.filter(Q(conversor_1_id=id) | Q(conversor_2_id=id))

    rooms = []
    for room in filtered_rooms:
        if room.conversor_1_id == str(id):
            # If the user is conversor_1, get conversor_2
            rooms.append({"name": room.conversor_2_name, "id": room.room_id})
        elif room.conversor_2_id == str(id):
            # If the user is conversor_2, get conversor_1
            rooms.append({"name": room.conversor_1_name, "id": room.room_id})

    return rooms


def get_messages_from_room_id(room_id):
    filtered_messages = Message.objects.filter(room_id=room_id)
    messages = []
    for message in filtered_messages:
        try:
            sender_name = (
                message.sender_user.first_name + " " + message.sender_user.last_name
            )
            sender_id = message.sender_user.id
        except Exception:
            sender_name = message.sender_organization.organization_name
            sender_id = str(message.sender_organization.organization_id)

        messages.append(
            {
                "sender_id": sender_id,
                "message_body": message.message_body,
                "sender_name": sender_name,
                "time": message.created_at,
            }
        )
    return messages


def get_curr_room(room_id, user_or_org_id):

    curr_room_obj = Room.objects.get(room_id=room_id)
    curr_room_name = ""
    curr_room_other_id = ""

    if curr_room_obj.conversor_1_id == str(user_or_org_id):
        curr_room_name = curr_room_obj.conversor_2_name
        curr_room_other_id = curr_room_obj.conversor_2_id
    elif curr_room_obj.conversor_2_id == str(user_or_org_id):
        curr_room_name = curr_room_obj.conversor_1_name
        curr_room_other_id = curr_room_obj.conversor_1_id

    curr_room = {
        "id": curr_room_obj.room_id,
        "name": curr_room_name,
        "other_user_id": curr_room_other_id,
    }
    return curr_room


@login_required
def messaging_view(request):
    user_id = request.user.id
    organizations = Organization.objects.all()
    rooms = get_rooms(user_id)

    return render(
        request,
        "messaging_dashboard.html",
        {"organizations": organizations, "rooms": rooms},
    )


@login_required
def get_messages(request, room_id):
    user_id = request.user.id
    curr_user = User.objects.get(id=user_id)
    organizations = Organization.objects.all()

    rooms = get_rooms(user_id)
    messages = get_messages_from_room_id(room_id)
    curr_room = get_curr_room(room_id, user_id)
    curr_room["sender_name"] = curr_user.first_name + " " + curr_user.last_name

    return render(
        request,
        "messaging_dashboard.html",
        {
            "organizations": organizations,
            "rooms": rooms,
            "curr_room": curr_room,
            "messages": messages,
        },
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
            conversor_1_name = sender.first_name + " " + sender.last_name
            conversor_2_type = ContentType.objects.get_for_model(receiver)
            conversor_2_id = receiver.organization_id
            conversor_2_name = receiver.organization_name

        elif sender_type == "organization" and receiver_type == "user":
            receiver = User.objects.get(id=receiver_id)
            sender = Organization.objects.get(organization_id=sender_id)
            room_id = f"{receiver_id}_{sender_id}"
            room_name = f"Chat with {receiver.first_name} and {sender}"
            conversor_1_type = ContentType.objects.get_for_model(sender)
            conversor_1_id = sender.organization_id
            conversor_1_name = sender.organization_name
            conversor_2_type = ContentType.objects.get_for_model(receiver)
            conversor_2_id = receiver.id
            conversor_2_name = receiver.first_name + " " + receiver.last_name

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
                conversor_1_name=conversor_1_name,
                conversor_2_name=conversor_2_name,
            )
            room.save()
            messages.success(request, f"Created a new chat with {receiver}")

        return redirect("messaging:messaging")
    return redirect("messaging:messaging")


@login_required
def org_messaging_view(request, organization_id):

    rooms = get_rooms(organization_id)
    return render(
        request,
        "messaging_dashboard.html",
        {"is_org": True, "organization_id": organization_id, "rooms": rooms},
    )


@login_required
def org_get_messages(request, organization_id, room_id):

    curr_org = Organization.objects.get(organization_id=organization_id)
    rooms = get_rooms(organization_id)
    messages = get_messages_from_room_id(room_id)
    curr_room = get_curr_room(room_id, organization_id)
    curr_room["sender_name"] = curr_org.organization_name

    return render(
        request,
        "messaging_dashboard.html",
        {
            "is_org": True,
            "organization_id": organization_id,
            "rooms": rooms,
            "curr_room": curr_room,
            "messages": messages,
        },
    )

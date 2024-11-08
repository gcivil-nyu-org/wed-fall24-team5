# your_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from database.models import Room, Message
from datetime import datetime
import uuid


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        # Join room group
        await self.channel_layer.group_add(self.room_id, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_id, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        print("kjsdn vlskjd ")
        text_data_json = json.loads(text_data)
        message = text_data_json
        message_id = str(uuid.uuid4())
        created_at = str(datetime.now())
        event = {
            "type": "send_message",
            "message": message,
            "message_id": message_id,
            "created_at": created_at,
        }
        print(event)
        await self.channel_layer.group_send(self.room_id, event)

    # Receive message from room group
    async def send_message(self, event):
        print("Sdilwekjbflsdkj")
        data = event["message"]

        message_id = event["message_id"]
        created_at = event["created_at"]
        await self.create_message(
            data=data, message_id=message_id, created_at=created_at
        )

        response_data = {
            "sender_id": data["sender_id"],
            "sender_name": data["sender_name"],
            "message_body": data["message"],
            "time": created_at,
        }
        await self.send(text_data=json.dumps({"message": response_data}))

    @database_sync_to_async
    def create_message(self, data, message_id, created_at):
        curr_room = Room.objects.get(room_id=data["room_id"])
        if not Message.objects.filter(message_id=message_id).exists():
            if not data["is_org"]:
                new_message = Message(
                    message_id=message_id,
                    created_at=created_at,
                    room=curr_room,
                    sender_user_id=data["sender_id"],
                    receiver_organization_id=data["receiver_id"],
                    message_body=data["message"],
                )
                new_message.save()
            else:
                new_message = Message(
                    message_id=message_id,
                    created_at=created_at,
                    room=curr_room,
                    sender_organization_id=data["sender_id"],
                    receiver_user_id=data["receiver_id"],
                    message_body=data["message"],
                )
                new_message.save()

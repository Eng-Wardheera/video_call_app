import datetime

from bson import ObjectId
from flask_mail import Message
from flask_socketio import join_room
from pycountry import db
from yaml import emit

from app import socketio
from app.modal import Call

online_users = {}
active_calls = {}

@socketio.on("join_call")
def join_call(data):
    user_id = data["id"]

    online_users[user_id] = {
        "id": user_id,
        "name": data["name"]
    }

    emit("online_users", list(online_users.values()), broadcast=True)

@socketio.on("send_message")
def send_message(data):
    msg = Message({
        "conversation_id": data.get("conversation_id"),
        "sender_id": data["from"]["id"],
        "receiver_id": data["to"]["id"],
        "content": data["text"],
        "type": "text",
        "status": "sent",
        "created_at": datetime.utcnow()
    })

    # 👉 SAVE TO MONGO
    db.messages.insert_one(msg.to_dict())

    emit("receive_message", {
        "from": data["from"]["name"],
        "text": data["text"]
    }, broadcast=True)

@socketio.on("start_call")
def start_call(data):
    caller = data["from"]
    receiver = data["to"]

    room = f"call_{caller['id']}_{receiver['id']}"

    active_calls[caller["id"]] = room
    active_calls[receiver["id"]] = room

    join_room(room)

    # 💾 SAVE CALL START
    call = Call({
        "caller_id": caller["id"],
        "receiver_id": receiver["id"],
        "call_type": "video",
        "status": "answered",
        "started_at": datetime.utcnow()
    })

    call_id = db.calls.insert_one(call.to_dict()).inserted_id

    emit("incoming_call", {
        "from": caller,
        "room": room,
        "call_id": str(call_id)
    }, room=room)



@socketio.on("end_call")
def end_call(data):
    call_id = data.get("call_id")

    if call_id:
        call = db.calls.find_one({"_id": ObjectId(call_id)})

        if call:
            ended_at = datetime.utcnow()

            duration = int((ended_at - call["started_at"]).total_seconds())

            db.calls.update_one(
                {"_id": ObjectId(call_id)},
                {"$set": {
                    "ended_at": ended_at,
                    "duration": duration,
                    "status": "ended"
                }}
            )

    emit("call_ended", {}, broadcast=True)



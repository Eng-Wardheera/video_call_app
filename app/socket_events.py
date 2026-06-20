import datetime
from bson import ObjectId
from flask import request
from flask_socketio import emit, join_room

from app import socketio, db
from app.modal import Call


online_users = {}
sid_map = {}
active_calls = {}


@socketio.on("join_call")
def join_call(data):

    user_id = str(data["id"])

    sid_map[request.sid] = user_id

    online_users[user_id] = {
        "id": user_id,
        "name": data["name"]
    }

    emit("online_users", list(online_users.values()), broadcast=True)

@socketio.on("disconnect")
def disconnect():

    user_id = sid_map.get(request.sid)

    if user_id:
        online_users.pop(user_id, None)
        sid_map.pop(request.sid, None)

        emit("online_users", list(online_users.values()), broadcast=True)


@socketio.on("send_message")
def send_message(data):

    if not data.get("to"):
        return

    message_doc = {
        "sender_id": data["from"]["id"],
        "receiver_id": data["to"]["id"],
        "content": data["text"],
        "type": "text",
        "status": "sent",
        "created_at": datetime.datetime.utcnow()
    }

    db.messages.insert_one(message_doc)

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

    call = Call({
        "caller_id": caller["id"],
        "receiver_id": receiver["id"],
        "call_type": "video",
        "status": "started",
        "started_at": datetime.datetime.utcnow()
    })

    call_id = db.calls.insert_one(call.to_dict()).inserted_id

    # ONLY SEND TO RECEIVER (FIX)
    emit("incoming_call", {
        "from": caller,
        "call_id": str(call_id)
    }, room=room)


@socketio.on("start_call")
def start_call(data):

    caller = data["from"]
    receiver = data["to"]

    room = f"call_{caller['id']}_{receiver['id']}"

    active_calls[caller["id"]] = room
    active_calls[receiver["id"]] = room

    join_room(room)

    call = Call({
        "caller_id": caller["id"],
        "receiver_id": receiver["id"],
        "call_type": "video",
        "status": "started",
        "started_at": datetime.datetime.utcnow()
    })

    call_id = db.calls.insert_one(call.to_dict()).inserted_id

    # ONLY SEND TO RECEIVER (FIX)
    emit("incoming_call", {
        "from": caller,
        "call_id": str(call_id)
    }, room=room)

    
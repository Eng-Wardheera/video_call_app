from decimal import Decimal
import enum
from bson import ObjectId
from flask_login import UserMixin
from datetime import datetime, timedelta
from app import now_eat



# 1. Qeexidda Enum-ka
class UserRole(enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    user = "user"




class User(UserMixin):
    def __init__(self, data):
        self.data = data or {}

        self.id = str(self.data.get("_id"))
        self.username = self.data.get("username")
        self.fullname = self.data.get("fullname")
        self.email = self.data.get("email")
        self.password = self.data.get("password")

        # Role system (Mongo style)
        self.role = self.data.get("role", "user")
        self.role_id = self.data.get("role_id")  # ObjectId string if using reference

        # Basic info
        self.phone = self.data.get("phone")
        self.country = self.data.get("country")
        self.city = self.data.get("city")
        self.state = self.data.get("state")
        self.address = self.data.get("address")
        self.bio = self.data.get("bio")
        self.photo = self.data.get("photo")
        self.gender = self.data.get("gender")
        self.photo_visibility = self.data.get("photo_visibility", "everyone")

        self.status = self.data.get("status", True)

        # Device info
        self.device = self.data.get("device")
        self.browser = self.data.get("browser")
        self.platform = self.data.get("platform")
        self.device_name = self.data.get("device_name")
        self.interface_name = self.data.get("interface_name")

        # Security
        self.is_verified = self.data.get("is_verified", False)
        self.auth_status = self.data.get("auth_status", "logout")
        self.session_token = self.data.get("session_token")
        self.login_time = self.data.get("login_time")
        self.last_seen = self.data.get("last_seen")

        self.phone_verified = self.data.get("phone_verified", False)
        self.two_factor_enabled = self.data.get("two_factor_enabled", False)
        self.two_factor_code = self.data.get("two_factor_code")
        self.two_factor_expires_at = self.data.get("two_factor_expires_at")

        self.last_login_ip = self.data.get("last_login_ip")
        self.remember_token = self.data.get("remember_token")
        self.failed_login_attempts = self.data.get("failed_login_attempts", 0)

        self.auth_provider = self.data.get("auth_provider", "local")
        self.last_active = self.data.get("last_active")

        # Socials
        self.facebook = self.data.get("facebook")
        self.twitter = self.data.get("twitter")
        self.google = self.data.get("google")
        self.whatsapp = self.data.get("whatsapp")
        self.instagram = self.data.get("instagram")
        self.github = self.data.get("github")
        self.github_id = self.data.get("github_id")

        # Timestamps
        self.created_at = self.data.get("created_at")
        self.updated_at = self.data.get("updated_at")

        # Embedded relationships (Mongo style)
        self.user_logs = self.data.get("user_logs", [])
        self.sessions = self.data.get("sessions", [])
        self.user_permissions = self.data.get("user_permissions", [])

        self.patient_appointments = self.data.get("patient_appointments", [])
        self.doctor_appointments = self.data.get("doctor_appointments", [])

    # Flask-Login required
    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.status is True

    @property
    def permissions(self):
        return [p.get("permission") for p in self.user_permissions]

    def to_dict(self):
        return self.data

    def __repr__(self):
        return f"<User {self.username}>"


class Message:
    def __init__(self, data: dict):
        data = data or {}

        self.id = str(data.get("_id")) if data.get("_id") else None

        self.conversation_id = data.get("conversation_id")

        self.sender_id = str(data.get("sender_id")) if data.get("sender_id") else None
        self.receiver_id = str(data.get("receiver_id")) if data.get("receiver_id") else None

        self.content = data.get("content")
        self.type = data.get("type", "text")  # text, image, file, video, audio

        self.status = data.get("status", "sent")  # sent, delivered, read

        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", datetime.utcnow())

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self):
        return f"<Message {self.id}>"


class Call:
    def __init__(self, data: dict):
        data = data or {}

        self.id = str(data.get("_id")) if data.get("_id") else None

        self.caller_id = str(data.get("caller_id")) if data.get("caller_id") else None
        self.receiver_id = str(data.get("receiver_id")) if data.get("receiver_id") else None

        self.call_type = data.get("call_type", "audio")  # audio, video
        self.status = data.get("status", "missed")  # answered, rejected, busy, missed

        self.started_at = data.get("started_at")
        self.ended_at = data.get("ended_at")

        self.duration = int(data.get("duration", 0))  # seconds

    def calculate_duration(self):
        if self.started_at and self.ended_at:
            self.duration = int((self.ended_at - self.started_at).total_seconds())
        return self.duration

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else None,
            "caller_id": self.caller_id,
            "receiver_id": self.receiver_id,
            "call_type": self.call_type,
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration": self.duration,
        }

    def __repr__(self):
        return f"<Call {self.id}>"
    


class Contact:
    def __init__(self, data):
        self.data = data or {}

        self.id = str(self.data.get("_id"))
        self.user_id = str(self.data.get("user_id")) if self.data.get("user_id") else None

        self.name = self.data.get("name")
        self.email = self.data.get("email")
        self.subject = self.data.get("subject")
        self.message = self.data.get("message")

        # ⭐ NEW
        self.rating = int(self.data.get("rating", 5))  # default 5 stars

        self.status = self.data.get("status", "pending")
        self.created_at = self.data.get("created_at")
        self.updated_at = self.data.get("updated_at")



class Session:
    def __init__(self, data):
        self.data = data or {}

        self.id = str(self.data.get("_id"))
        self.user_id = str(self.data.get("user_id"))

        self.session_token = self.data.get("session_token")
        self.ip = self.data.get("ip")
        self.device = self.data.get("device")

        self.created_at = self.data.get("created_at", datetime.utcnow())
        self.expires_at = self.data.get(
            "expires_at",
            datetime.utcnow() + timedelta(days=7)
        )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def is_active(self):
        return not self.is_expired()

    def to_dict(self):
        return {
            "_id": self.id,
            "user_id": self.user_id,
            "session_token": self.session_token,
            "ip": self.ip,
            "device": self.device,
            "created_at": self.created_at,
            "expires_at": self.expires_at
        }

    def __repr__(self):
        return f"<Session {self.session_token}>"



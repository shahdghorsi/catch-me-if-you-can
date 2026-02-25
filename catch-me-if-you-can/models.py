from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets

db = SQLAlchemy()

# Vibe statuses
VIBE_AVAILABLE = 'available'      # Green glow - open for anything
VIBE_QUICK_CHAT = 'quick_chat'    # Yellow glow - just a quick coffee
VIBE_FOCUSED = 'focused'          # Gray glow - busy but visible


class User(db.Model):
    """User model for tracking people's locations."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar_emoji = db.Column(db.String(10), nullable=True)
    team = db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    floor = db.Column(db.Integer, nullable=True)
    vibe = db.Column(db.String(20), default=VIBE_AVAILABLE)
    status = db.Column(db.String(50), nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'avatar_emoji': self.avatar_emoji,
            'team': self.team or '',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'floor': self.floor,
            'vibe': self.vibe or VIBE_AVAILABLE,
            'status': self.status or '',
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_active': self.is_active
        }


class TagRequest(db.Model):
    """Tag request - someone saying 'I'll join you in 5 min'"""

    __tablename__ = 'tag_requests'

    id = db.Column(db.Integer, primary_key=True)
    tagger_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tagged_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, connected, expired
    connected_at = db.Column(db.DateTime, nullable=True)

    tagger = db.relationship('User', foreign_keys=[tagger_id], backref='tags_sent')
    tagged = db.relationship('User', foreign_keys=[tagged_id], backref='tags_received')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(minutes=5)

    def to_dict(self):
        return {
            'id': self.id,
            'tagger': self.tagger.to_dict() if self.tagger else None,
            'tagged': self.tagged.to_dict() if self.tagged else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status,
            'seconds_remaining': max(0, int((self.expires_at - datetime.utcnow()).total_seconds())) if self.expires_at else 0
        }

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at if self.expires_at else True


class MagicLink(db.Model):
    """Magic link for email verification."""

    __tablename__ = 'magic_links'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    team = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    used = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(minutes=15)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at if self.expires_at else True

    @property
    def is_valid(self):
        return not self.used and not self.is_expired

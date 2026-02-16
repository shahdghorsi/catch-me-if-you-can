import os
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit

from models import db, User, TagRequest, VIBE_AVAILABLE
from geo_utils import haversine_distance

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///office.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Fun emoji avatars for users
AVATAR_EMOJIS = [
    '😀', '😎', '🤓', '🥳', '🤠', '🦊', '🐱', '🐶', '🦁', '🐸',
    '🐵', '🤖', '👽', '🎃', '🦄', '🐼', '🐨', '🐯', '🦋', '🐙',
    '🦖', '🦕', '🐲', '🧙', '🧛', '🦸', '🦹', '🧚', '🌟', '⚡'
]

# Connection distance threshold (meters) - how close to "connect"
CONNECTION_DISTANCE = 30


def get_random_emoji():
    return random.choice(AVATAR_EMOJIS)


def get_active_people():
    """Get all active people with location."""
    return [u.to_dict() for u in User.query.filter_by(is_active=True).filter(User.latitude.isnot(None)).all()]


def get_active_tags():
    """Get all pending tag requests."""
    tags = TagRequest.query.filter_by(status='pending').all()
    # Clean up expired tags
    for tag in tags:
        if tag.is_expired:
            tag.status = 'expired'
    db.session.commit()
    return [t.to_dict() for t in TagRequest.query.filter_by(status='pending').all()]


def broadcast_state():
    """Broadcast full state to all clients."""
    socketio.emit('state_update', {
        'people': get_active_people(),
        'tags': get_active_tags()
    })


def check_connection(tag):
    """Check if tagger and tagged are close enough to connect."""
    if not tag.tagger or not tag.tagged:
        return False
    if not tag.tagger.latitude or not tag.tagged.latitude:
        return False

    distance = haversine_distance(
        tag.tagger.latitude, tag.tagger.longitude,
        tag.tagged.latitude, tag.tagged.longitude
    )
    return distance <= CONNECTION_DISTANCE


# Routes
@app.route('/')
def index():
    return render_template('index.html')


def validate_work_email(email):
    import re
    pattern = r'^[a-zA-Z]+\.[a-zA-Z]+@virginmediao2\.co\.uk$'
    return re.match(pattern, email) is not None


def name_from_email(email):
    local_part = email.split('@')[0]
    parts = local_part.split('.')
    return ' '.join(part.capitalize() for part in parts)


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        team = request.form.get('team', '').strip()

        if not email:
            return render_template('checkin.html', error="Please enter your work email")

        if not validate_work_email(email):
            return render_template('checkin.html', error="Please use your work email (name.surname@virginmediao2.co.uk)")

        if not team:
            return render_template('checkin.html', error="Please select your team")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            existing_user.is_active = True
            existing_user.last_seen = datetime.utcnow()
            existing_user.team = team  # Update team in case they changed
            db.session.commit()
            socketio.emit('user_dropped_in', existing_user.to_dict())
            return redirect(url_for('index', user_id=existing_user.id))

        name = name_from_email(email)
        user = User(email=email, name=name, avatar_emoji=get_random_emoji(), team=team, is_active=True)
        db.session.add(user)
        db.session.commit()

        socketio.emit('user_dropped_in', user.to_dict())
        return redirect(url_for('index', user_id=user.id))

    return render_template('checkin.html')


@app.route('/api/state')
def api_state():
    """Get current state - people and active tags."""
    return jsonify({
        'people': get_active_people(),
        'tags': get_active_tags()
    })


@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('register_user')
def handle_register_user(data):
    user_id = data.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.is_active = True
            user.last_seen = datetime.utcnow()
            db.session.commit()
            broadcast_state()


@socketio.on('location_update')
def handle_location_update(data):
    user_id = data.get('user_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not user_id or latitude is None or longitude is None:
        return

    user = User.query.get(user_id)
    if not user:
        return

    user.latitude = latitude
    user.longitude = longitude
    user.last_seen = datetime.utcnow()
    user.is_active = True
    db.session.commit()

    # Check if this user has any pending tags that might now be connected
    pending_tags = TagRequest.query.filter(
        ((TagRequest.tagger_id == user_id) | (TagRequest.tagged_id == user_id)),
        TagRequest.status == 'pending'
    ).all()

    for tag in pending_tags:
        if check_connection(tag):
            tag.status = 'connected'
            tag.connected_at = datetime.utcnow()
            db.session.commit()
            # Emit connection celebration to both users
            socketio.emit('connection_made', {
                'tag': tag.to_dict(),
                'tagger_id': tag.tagger_id,
                'tagged_id': tag.tagged_id
            })

    broadcast_state()


@socketio.on('set_vibe')
def handle_set_vibe(data):
    """Set user's vibe status."""
    user_id = data.get('user_id')
    vibe = data.get('vibe')

    if not user_id or not vibe:
        return

    user = User.query.get(user_id)
    if user:
        user.vibe = vibe
        db.session.commit()
        broadcast_state()


@socketio.on('set_status')
def handle_set_status(data):
    """Set user's custom status."""
    user_id = data.get('user_id')
    status = data.get('status', '')

    if not user_id:
        return

    user = User.query.get(user_id)
    if user:
        # Limit status length
        user.status = status[:50] if status else None
        db.session.commit()
        broadcast_state()


@socketio.on('tag_user')
def handle_tag_user(data):
    """Handle 'I'll join you in 5 min' tag."""
    tagger_id = data.get('tagger_id')
    tagged_id = data.get('tagged_id')

    if not tagger_id or not tagged_id or tagger_id == tagged_id:
        return

    tagger = User.query.get(tagger_id)
    tagged = User.query.get(tagged_id)

    if not tagger or not tagged:
        return

    # Check if there's already a pending tag between these users
    existing = TagRequest.query.filter(
        ((TagRequest.tagger_id == tagger_id) & (TagRequest.tagged_id == tagged_id)) |
        ((TagRequest.tagger_id == tagged_id) & (TagRequest.tagged_id == tagger_id)),
        TagRequest.status == 'pending'
    ).first()

    if existing:
        return  # Already have a pending tag

    # Create new tag
    tag = TagRequest(tagger_id=tagger_id, tagged_id=tagged_id)
    db.session.add(tag)
    db.session.commit()

    # Notify both users
    socketio.emit('tagged', {
        'tag': tag.to_dict(),
        'tagger_id': tagger_id,
        'tagged_id': tagged_id
    })

    broadcast_state()


@socketio.on('user_inactive')
def handle_user_inactive(data):
    user_id = data.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            socketio.emit('user_left', {'user_id': user_id, 'name': user.name})
            broadcast_state()


# Initialize database
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)

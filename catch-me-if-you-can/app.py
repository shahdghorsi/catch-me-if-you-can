from gevent import monkey
monkey.patch_all()

import os
import random
import resend
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit

from models import db, User, TagRequest, MagicLink, VIBE_AVAILABLE
from geo_utils import haversine_distance

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///office.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

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
    # Requires format: name.surname@virginmediao2.co.uk OR allow test email
    test_email = os.environ.get('TEST_EMAIL', '')
    if test_email and email.lower() == test_email.lower():
        return True
    pattern = r'^[a-zA-Z]+\.[a-zA-Z]+@virginmediao2\.co\.uk$'
    return re.match(pattern, email) is not None


def name_from_email(email):
    local_part = email.split('@')[0]
    parts = local_part.split('.')
    if len(parts) == 1:
        return parts[0].capitalize()
    return ' '.join(part.capitalize() for part in parts)


def send_magic_link_email(email, token, base_url):
    """Send magic link email to user via Resend."""
    resend_api_key = os.environ.get('RESEND_API_KEY', '')
    from_email = os.environ.get('FROM_EMAIL', 'onboarding@resend.dev')

    verify_url = f"{base_url}/verify/{token}"
    name = name_from_email(email).split()[0]

    if not resend_api_key:
        print(f"[DEV MODE] Magic link for {email}: {verify_url}")
        return True  # Dev mode - just log the link

    resend.api_key = resend_api_key

    html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; background: #f5f5f5;">
        <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; padding: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h1 style="margin: 0 0 20px; font-size: 28px;">🏃‍♂️ Hey {name}!</h1>
            <p style="color: #666; font-size: 16px; line-height: 1.6;">
                Click the button below to sign in to <strong>Catch Me If You Can</strong> and let your colleagues find you!
            </p>
            <a href="{verify_url}" style="display: inline-block; margin: 30px 0; padding: 16px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px;">
                Sign In →
            </a>
            <p style="color: #999; font-size: 14px;">
                This link expires in 15 minutes.<br>
                If you didn't request this, just ignore this email.
            </p>
        </div>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [email],
            "subject": "🔐 Your sign-in link for Catch Me If You Can",
            "html": html
        })
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


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

        # Create magic link
        magic_link = MagicLink(email=email, team=team)
        db.session.add(magic_link)
        db.session.commit()

        # Send email
        base_url = request.host_url.rstrip('/')
        if send_magic_link_email(email, magic_link.token, base_url):
            return render_template('checkin_sent.html', email=email)
        else:
            return render_template('checkin.html', error="Failed to send email. Please try again.")

    return render_template('checkin.html')


@app.route('/verify/<token>')
def verify_magic_link(token):
    """Verify magic link and log user in."""
    magic_link = MagicLink.query.filter_by(token=token).first()

    if not magic_link:
        return render_template('verify_error.html', error="Invalid link. Please request a new one.")

    if magic_link.used:
        return render_template('verify_error.html', error="This link has already been used. Please request a new one.")

    if magic_link.is_expired:
        return render_template('verify_error.html', error="This link has expired. Please request a new one.")

    # Mark link as used
    magic_link.used = True
    db.session.commit()

    email = magic_link.email
    team = magic_link.team

    # Find or create user
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        existing_user.is_active = True
        existing_user.last_seen = datetime.utcnow()
        if team:
            existing_user.team = team
        db.session.commit()
        socketio.emit('user_dropped_in', existing_user.to_dict())
        return redirect(url_for('index', user_id=existing_user.id))

    name = name_from_email(email)
    user = User(email=email, name=name, avatar_emoji=get_random_emoji(), team=team, is_active=True)
    db.session.add(user)
    db.session.commit()

    socketio.emit('user_dropped_in', user.to_dict())
    return redirect(url_for('index', user_id=user.id))


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


@socketio.on('set_floor')
def handle_set_floor(data):
    """Set user's current floor in the office."""
    user_id = data.get('user_id')
    floor = data.get('floor')

    if not user_id:
        return

    user = User.query.get(user_id)
    if user:
        # Validate floor (1-9 or None to clear)
        if floor is None or (isinstance(floor, int) and 1 <= floor <= 9):
            user.floor = floor
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

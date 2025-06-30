from app import app, db, login_manager
from app.classes.data import User
from datetime import datetime, timezone
from flask import redirect, flash, request, session, url_for, render_template, abort
from functools import wraps
from authlib.integrations.flask_client import OAuth
import os
from flask_login import login_user, current_user
from sqlalchemy import select
from is_safe_url  import is_safe_url

# Google OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('ccpa_google_client_id'),
    client_secret=os.environ.get('ccpa_google_client_secret'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.before_request
def before_request():

    # this checks if the user requests http and if they did it changes it to https
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)

def create_or_update_user(user_info):
    """Create or update user in database"""
    try:
        # Check if user exists
        user = User.query.filter_by(google_id=user_info['sub']).first()
        
        if user:
            # Update existing user
            user.last_login = datetime.now(timezone.utc)
            user.name = user_info['name']
            user.picture = user_info.get('picture')
        else:
            # Create new user
            user = User(
                google_id=user_info['sub'],
                email=user_info['email'],
                name=user_info['name'],
                picture=user_info.get('picture'),
                last_login=datetime.now(timezone.utc)
            )
            db.session.add(user)
        
        db.session.commit()
        return user
        
    except Exception as e:
        db.session.rollback()
        raise e

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@login_manager.user_loader
def load_user(id):
    return select(User).where(User.id == id)

@app.route('/login/callback')
def callback():
    """Handle OAuth callback"""
    try:
        token = google.authorize_access_token()
        user_info = token['userinfo']
        
        # Create or update user in database
        user = create_or_update_user(user_info)

        login_user(user)
        load_user(user.id)
        
        # Store user info in session
        session['user'] = {
            'id': user.id,
            'google_id': user.google_id,
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        }
        flash(session['user'])
        
        flash('Successfully logged in!', 'success')

        next = request.args.get('next')
        # url_has_allowed_host_and_scheme should check if the url is safe
        # for redirects, meaning it matches the request host.
        # See Django's url_has_allowed_host_and_scheme for an example.
        if next and is_safe_url(next, request.host):
            return abort(400)

        return redirect(next or url_for('dashboard'))
        
    except Exception as e:
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard page"""
    return render_template('dashboard.html', user=session['user'])

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = User.query.get(session['user']['id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('logout'))
    
    return render_template('profile.html', user=user.to_dict())

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/users')
@login_required
def list_users():
    """Admin page to list all users (for demo purposes)"""
    users = User.query.order_by(User.created_at.desc()).all()
    users_data = [user.to_dict() for user in users]
    
    return render_template('users.html', users=users_data)


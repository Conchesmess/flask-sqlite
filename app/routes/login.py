from app import app, db, login_manager
from app.classes.data import User
from datetime import datetime, timezone
from flask import redirect, flash, request, session, url_for, render_template, abort
from functools import wraps
from authlib.integrations.flask_client import OAuth
import os
from flask_login import login_user, current_user, login_required, logout_user
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
    thisUser=None
    try:
        # Check if user exists
        thisUser = db.one_or_404(db.select(User).filter_by(google_id=user_info['sub']))
    
    except:
        # Create new user
        thisUser = User(
            google_id=user_info['sub'],
            email=user_info['email'],
            name=user_info['name'],
            picture=user_info.get('picture'),
            last_login=datetime.now(timezone.utc)
        )
        db.session.add(thisUser)
    else:
        # Update existing user
        thisUser.last_login = datetime.now(timezone.utc)
    db.session.commit()
    return thisUser
        

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@login_manager.user_loader
def load_user(id):
    try:
        user = db.one_or_404(db.select(User).where(User.id == id))
        return user

    except:
        flash(f"No user was loaded.")


@app.route('/login/callback')
def callback():
    """Handle OAuth callback"""
    try:
        token = google.authorize_access_token()
        #session['google_id_token'] = token['id_token']
        current_user.google_id_token = token['id_token']
        user_info = token['userinfo']
        
    except Exception as e:
         flash(f'Login failed: {str(e)}', 'error')
         return redirect(url_for('index'))
    
    else:
        # Create or update user in database
        user = create_or_update_user(user_info)
        login_user(user, force=True)
        load_user(user.id)
        
        flash(f"current user is authenticated: {current_user.is_authenticated}","success")
        #flash(f"Current user has valid google id token: {current_user.is_valid()}","success")

        next = request.args.get('next')
        # url_has_allowed_host_and_scheme should check if the url is safe
        # for redirects, meaning it matches the request host.
        # See Django's url_has_allowed_host_and_scheme for an example.
        if next and is_safe_url(next, request.host):
            return abort(400)
    return redirect(next or url_for('profile'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    if current_user.is_anonymous:
        flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/users')
@login_required
def list_users():
    """Admin page to list all users (for demo purposes)"""
    users = User.query.order_by(User.created_at.desc()).all()
    users_data = [user.to_dict() for user in users]
    
    return render_template('users.html', users=users_data)

@app.route(('/valid'))
@login_required
def valid():
    if current_user.is_valid():
        flash("Current User has a valid Google Login.","info")
        return redirect(url_for("profile"))
    else:
        flash("Current User needed to refresh Google Credentials.","info")
        return redirect(url_for('login'))
    

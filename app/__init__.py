from flask import Flask, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask_moment import Moment


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

moment = Moment(app)

# confirm Delete Decorator
def confirm_delete(model_class, redirect_url=None, message_field='name'):
    """
    Advanced version that automatically fetches the model instance.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the item ID from route parameters
            item_id = kwargs.get('id')
            if not item_id:
                flash('No item ID provided', 'error')
                return redirect(redirect_url or '/')
            
            # Fetch the item
            item = model_class.query.get_or_404(item_id)
            
            # Check if this is a confirmation request
            if request.method == 'POST' and request.form.get('confirm_delete') == 'true':
                # User confirmed, proceed with deletion
                return f(*args, **kwargs)
            
            # Show confirmation dialog
            display_name = getattr(item, message_field, str(item))
            
            return render_template(
                "delete.html",
                item=item,
                display_name=display_name,
                current_url=request.url,
                cancel_url=redirect_url or request.referrer or '/'
            )
        
        return decorated_function
    return decorator

from .routes import *

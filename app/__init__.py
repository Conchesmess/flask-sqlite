from flask import Flask, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps
from flask_moment import Moment
from markupsafe import Markup
from datetime import datetime


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

login_manager = LoginManager(app)
# login_manager = LoginManager()
# login_manager.init_app(app)

moment = Moment(app)

from app.classes.flaskmodals import Modal, render_template_modal
modal = Modal(app)


# confirm Delete Decorator
def confirm_delete(model_class, redirect_url=None, message_fields=[], message_date_field=None):
    """
    Advanced version that automatically fetches the model instance.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ajax = '_ajax' in request.form  # Add this line
            if ajax:        # Add these
                return ''   # two lines

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
            display_name=''


            for field in message_fields:
                thisAttribute = getattr(item,field,str(item))
                try:
                    len(thisAttribute)
                except TypeError:
                    pass
                else:
                    thisAttribute = thisAttribute[:100]
                display_name += f"<b> {str(field)}: </b> {thisAttribute} <br>"

            display_name = Markup(display_name)

            message_date = getattr(item,message_date_field,str(item))
            
            return render_template_modal(
                "delete_modal.html",
                item=item,
                display_name=display_name,
                current_url=request.url,
                message_date = message_date,
                cancel_url=redirect_url or request.referrer or '/'
            )
        
        return decorated_function
    return decorator


from .routes import *

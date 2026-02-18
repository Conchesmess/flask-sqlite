def modal_messages():
def render_template_modal(*args, **kwargs):
def can_stream():

# This file adds modal features to the app.
# Modals are pop-up windows for messages or forms.

from functools import wraps  # For decorators
from flask import (Blueprint, render_template, get_flashed_messages, request)  # Flask tools
from jinja2.utils import markupsafe  # For safe HTML
from .partial import get_partial  # Get modal content
from flask import current_app  # Current app

# Show modal messages in templates
def modal_messages():
    '''This will be available in the app templates for use in the modal body.'''
    return markupsafe.Markup(render_template('modals/modalMessages.html'))

# Render a template with a modal
def render_template_modal(*args, **kwargs):
    '''Call this function instead of render_template when the page contains a modal form.
    It accepts all the arguments passed to `render_template` apart from `modal` which is the `id` of the modal.'''
    ctx = current_app._get_current_object() 
    modal = kwargs.pop('modal', 'modal-form')

    if can_stream():
        # Prevent flash messages from showing both outside and inside the modal
        ctx._modal = True
        partial = get_partial(modal, *args, **kwargs)
        return f'<template>{partial}</template>'
    else:
        return render_template(*args, **kwargs)

# Check if the client accepts streams
def can_stream():
    '''Returns `True` if the client accepts streams.'''


    return 'text/modal-stream.html' in request.accept_mimetypes.values()



# Decorator to make using modals easier in view functions
def response(template=None):
    '''Use this decorator if coding render_template_modal in a number of places in a view function looks verbose.'''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = f"{request.endpoint.replace('.', '/')}.html"
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template_modal(template_name, **ctx)
        return decorated_function
    return decorator



# Modal class: sets up modal features for the app
class Modal:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    # Initialize modal features
    def init_app(self, app):
        '''Initialize the extension.
        Call method for blueprint and register template globals for app.'''
        self.register_blueprint(app)
        app.add_template_global(modal_messages)
        app.jinja_env.globals['modals'] = self.load
        app.jinja_env.globals['show_flashed_messages'] = self.show_flashed_messages

    # Register modal blueprint
    def register_blueprint(self, app):
        bp = Blueprint('modals', __name__, template_folder='templates',
                       static_folder='static',
                       static_url_path='/modals/static')
        app.register_blueprint(bp)

    # Show flash messages only if modal is active
    @staticmethod
    def show_flashed_messages(*args, **kwargs):
        '''Delegate to get_flashed_messages if _modal is set on the app context.'''
        ctx = current_app._get_current_object() 
        if not getattr(ctx, '_modal', None):
            return
        return get_flashed_messages(*args, **kwargs)

    # Load modal HTML templates
    def load(self):
        '''Load the following markup:
        1. nprogress.html - NProgress js library for progress bar
        2. jstemplate.html - Load js for fetch call'''
        nprogress_html = render_template('modals/nprogress.html')
        main_html = render_template('modals/jstemplate.html')
        html = markupsafe.Markup(nprogress_html + main_html)
        return html

# User Model
from app import db, client_id
from datetime import datetime, timezone
from flask_login import UserMixin, current_user
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import flash, session

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    picture = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    #is_active = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
            'created_at': self.created_at,
            'last_login': self.last_login
            #'is_active' : self.is_active
        }
    
    # def is_anonymous(self):
    #     if not current_user.id:
    #         return True
    #     else:
    #         return False

    # def is_authenticated(self):
    #     if current_user.id:
    #         return True
    #     else:
    #         return False
        
    def is_valid(self):
        try:
            # Specify the WEB_CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(current_user.google_id_token, requests.Request(), client_id)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [WEB_CLIENT_ID_1, WEB_CLIENT_ID_2, WEB_CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            # If the request specified a Google Workspace domain
            # if idinfo['hd'] != DOMAIN_NAME:
            #     raise ValueError('Wrong domain name.')
            
        except:
            # Invalid token
            return False
        else:
            # ID token is valid. Get the user's Google Account ID from the decoded token.
            return True

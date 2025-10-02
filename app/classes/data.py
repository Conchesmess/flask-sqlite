from datetime import datetime, timezone
from flask_login import UserMixin, current_user
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email_ousd = db.Column(db.String(120), unique=True, nullable=False)
    email_personal = db.Column(db.String(120), unique=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200))
    mobile = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    aeriesid = db.Column(db.Integer)
    gid = db.Column(db.String(50))
    role = db.Column(db.String(20)) #staff, teacher, student

    # Related data
    stories = db.relationship('Story', back_populates='author')


    
    def __repr__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email_ousd': self.email_ousd,
            'email_ersonal': self.email_personal,
            'fname': self.fname,
            'lname': self.lname,
            'image': self.image,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
        
    def is_valid(self):
        try:
            # Specify the WEB_CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(current_user.google_id_token, requests.Request(), os.environ.get('ccpa_google_client_id'))

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
        
class Story(db.Model):
    __tablename__ = 'story'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    title = db.Column(db.String(100))
    createdate = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='stories')



class GoogleClassroom(db.Model):
    __tablename__ = 'google_classroom'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    teacher = db.relationship('User')

    gteacherdict = db.Column(db.JSON)
    gclassdict = db.Column(db.JSON)
    # courseworkdict values: https://developers.google.com/classroom/reference/rest/v1/courses.courseWork
    courseworkdict = db.Column(db.JSON)
    courseworkupdate = db.Column(db.DateTime)

    studsubsdict = db.Column(db.JSON)
    studsubsupdate = db.Column(db.DateTime)

    gclassid = db.Column(db.String(100), unique=True)

    #list of possible cohorts for a class ie p3, p4
    sortcohorts = db.Column(db.JSON)

    #From Google Classroom
    grosterTemp = db.Column(db.JSON)

    aeriesid = db.Column(db.String(100))
    aeriesname = db.Column(db.String(100))
    pers = db.Column(db.JSON)

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_number = db.Column(db.String(100), unique=True, nullable=False)
    course_title = db.Column(db.String(200))
    course_name = db.Column(db.String(200))
    course_ag_requirement = db.Column(db.String(100))
    course_difficulty = db.Column(db.String(100))
    course_department = db.Column(db.String(100))
    course_pathway = db.Column(db.String(100))
    course_gradelevel = db.Column(db.String(50))
    create_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    modify_date = db.Column(db.DateTime)

    # Optional: Add indexes for course_name and course_title
    __table_args__ = (
        db.Index('idx_course_name_title', 'course_name', 'course_title'),
    )

# a join table between GoogleClassroom and User
class GEnrollment(db.Model):
    __tablename__ = 'genrollment'

    id = db.Column(db.Integer, primary_key=True)
    gclassroom_id = db.Column(db.Integer, db.ForeignKey('google_classroom.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    createdate = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    status = db.Column(db.String(50), default='~~~') # Created by student active, inactive, ignore
    classnameByUser = db.Column(db.String(200))
    nummissingupdate = db.Column(db.DateTime)
    missingasses = db.Column(db.JSON)
    missinglink = db.Column(db.String(200))
    sortCohort = db.Column(db.String(50), default='~')
    submissionsupdate = db.Column(db.DateTime)
    mysubmissions = db.Column(db.JSON)
    myassignments = db.Column(db.JSON)

    # Relationships
    gclassroom = db.relationship('GoogleClassroom', backref='enrollments')
    owner = db.relationship('User', backref='enrollments')

    __table_args__ = (
        db.UniqueConstraint('gclassroom_id', 'owner_id', name='uq_genrollment_gclassroom_owner'),
    )
from re import S
from app import app, db
from .login import credentials_to_dict
from flask import render_template, redirect, session, flash, url_for
from markupsafe import Markup
from app.classes.data import User
from app.classes.data import Course
from app.classes.data import GoogleClassroom, GEnrollment
from app.classes.forms import SimpleForm, SortOrderCohortForm
from datetime import datetime as dt
#from mongoengine.errors import NotUniqueError, DoesNotExist
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import google.oauth2.credentials
import googleapiclient.discovery
from google.auth.exceptions import RefreshError
from flask_login import current_user
#from app.routes.sbg import getCourseWork

# this function exists to update or create active google classrooms for the current user
# Teacher or student
@app.route('/getgclasses')
def getgclasses():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    elif not google.oauth2.credentials.Credentials(**session['credentials']).valid:
        return redirect(url_for('authorize'))
    else:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    classroom_service = googleapiclient.discovery.build('classroom', 'v1', credentials=credentials)
    try:
        gCourses = classroom_service.courses().list(courseStates='ACTIVE').execute()
    except RefreshError:
        flash("When I asked for the courses from Google Classroom I found that your credentials needed to be refreshed.")
        return redirect('/authorize')
    else:
        gCourses = gCourses['courses']

    for gCourse in gCourses:
        # Get the teacher record from Google API
        try:
            GClassTeacher = classroom_service.userProfiles().get(userId=gCourse['ownerId']).execute()
        except Exception:
            GClassTeacher = None

        # See if the teacher has a record on OTData site
        otdataGClassTeacher = User.query.filter_by(gid=gCourse['ownerId']).first()

        # Check to see if this course is saved in OTData
        otdataGCourse = GoogleClassroom.query.filter_by(gclassid=gCourse['id']).first()

        # If the GCourse IS NOT in OTData and the teacher IS in OTData
        if not otdataGCourse and otdataGClassTeacher:
            otdataGCourse = GoogleClassroom(
                gclassdict=gCourse,
                gteacherdict=GClassTeacher,
                gclassid=gCourse['id'],
                teacher=otdataGClassTeacher
            )
            db.session.add(otdataGCourse)
            db.session.commit()

        # If there is NOT a teacher in OTData and NOT a course in OTData
        elif not otdataGCourse and not otdataGClassTeacher:
            otdataGCourse = GoogleClassroom(
                gclassdict=gCourse,
                gteacherdict=GClassTeacher,
                gclassid=gCourse['id']
            )
            db.session.add(otdataGCourse)
            db.session.commit()

        # If the GCourse and the teacher are in OTData then update it
        elif otdataGCourse and otdataGClassTeacher:
            otdataGCourse.gclassdict = gCourse
            otdataGCourse.gteacherdict = GClassTeacher
            otdataGCourse.teacher = otdataGClassTeacher
            db.session.commit()

        # If the course is in OTData but the teacher is not in OTData
        elif otdataGCourse and not otdataGClassTeacher:
            otdataGCourse.gclassdict = gCourse
            otdataGCourse.gteacherdict = GClassTeacher
            db.session.commit()

        # Check for an enrollment. If not there, create one.
        userEnrollment = GEnrollment.query.filter_by(owner_id=current_user.id, gclassroom_id=otdataGCourse.id).first() if otdataGCourse else None
        if not userEnrollment and otdataGCourse:
            userEnrollment = GEnrollment(
                owner_id=current_user.id,
                gclassroom_id=otdataGCourse.id
            )
            db.session.add(userEnrollment)
            db.session.commit()

    return redirect(url_for('checkin'))


# this function exists to update the stored values for one or more google classrooms
@app.route('/gclasses')
def gclasses(gclassid=None):
    currUser = current_user

    # setup the Google API access credentials
    if google.oauth2.credentials.Credentials(**session['credentials']).valid:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    else:
        return redirect('/authorize')
    session['credentials'] = credentials_to_dict(credentials)
    classroom_service = googleapiclient.discovery.build('classroom', 'v1', credentials=credentials)

    # Get all of the google classes
    try:
        gCourses = classroom_service.courses().list(courseStates='ACTIVE').execute()
    except RefreshError:
        flash("When I asked for the courses from Google Classroom I found that your credentials needed to be refreshed.")
        return redirect('/authorize')
    else:
        gCourses = gCourses['courses']

    # Iterate through the classes
    for gCourse in gCourses:
        # get the teacher record from Google API
        try:
            GClassTeacher = classroom_service.userProfiles().get(userId=gCourse['ownerId']).execute()
        except Exception:
            GClassTeacher = None

        # See if the teacher has a record on OTData site
        otdataGClassTeacher = User.query.filter_by(gid=gCourse['ownerId']).first()

        # Check to see if this course is saved in OTData
        otdataGCourse = GoogleClassroom.query.filter_by(gclassid=gCourse['id']).first()

        # if the GCourse IS NOT in OTData and the teacher IS in the OTData
        if not otdataGCourse and otdataGClassTeacher:
            otdataGCourse = GoogleClassroom(
                gclassdict=gCourse,
                gteacherdict=GClassTeacher,
                gclassid=gCourse['id'],
                teacher=otdataGClassTeacher
            )
            db.session.add(otdataGCourse)
            db.session.commit()

        # If there is NOT a teacher in OTData and NOT a course in OTData
        elif not otdataGCourse and not otdataGClassTeacher:
            otdataGCourse = GoogleClassroom(
                gclassdict=gCourse,
                gteacherdict=GClassTeacher,
                gclassid=gCourse['id']
            )
            db.session.add(otdataGCourse)
            db.session.commit()

        # if the GCourse and the teacher is in OTData then update it
        elif otdataGCourse and otdataGClassTeacher:
            otdataGCourse.gclassdict = gCourse
            otdataGCourse.gteacherdict = GClassTeacher
            otdataGCourse.teacher = otdataGClassTeacher
            db.session.commit()

        # if the course is in OTData but the teacher is not in otdata
        elif otdataGCourse and not otdataGClassTeacher:
            otdataGCourse.gclassdict = gCourse
            otdataGCourse.gteacherdict = GClassTeacher
            db.session.commit()

        # Check to see if the class exists in the current user's enrollments
        userEnrollment = GEnrollment.query.filter_by(owner_id=currUser.id, gclassroom_id=otdataGCourse.id).first() if otdataGCourse else None

        # if the class does not exist then add it to the enrollments
        if not userEnrollment and otdataGCourse:
            newEnrollment = GEnrollment(
                owner_id=currUser.id,
                gclassroom_id=otdataGCourse.id,
                classnameByUser=otdataGCourse.gclassdict.get('name', ''),
                status='Inactive'
            )
            db.session.add(newEnrollment)
            db.session.commit()

    return redirect(url_for('checkin'))


@app.route("/roster/<gclassid>/<sort>", methods=['GET','POST'])
@app.route("/roster/<gclassid>", methods=['GET','POST'])
def roster(gclassid, sort="cohort"):
    # Get the GoogleClassroom by gclassid
    gclassroom = GoogleClassroom.query.filter_by(gclassid=gclassid).first()
    if not gclassroom:
        flash(Markup(f"You need to <a href='/getroster/{gclassid}'>update your roster from Google Classroom</a>."))
        return redirect(url_for('checkin'))

    # Get enrollments for this classroom
    enrollments = GEnrollment.query.filter_by(gclassroom_id=gclassroom.id).all()

    otdstus = []
    for enrollment in enrollments:
        owner = enrollment.owner
        try:
            role = owner.role.lower() if owner and owner.role else None
        except Exception:
            db.session.delete(enrollment)
            db.session.commit()
            continue
        else:
            if role == 'student' and owner.lname and owner.fname:
                otdstus.append(enrollment)
            elif role == 'student':
                flash(f"Something's wrong with this student's record so they were not included in the roster: {owner.email_ousd}")

    if sort == "cohort":
        try:
            otdstus = sorted(otdstus, key=lambda i: (i.sortCohort, i.owner.lname, i.owner.fname))
        except Exception as error:
            flash(f"Sort failed in the roster route with error: {error}")
    else:
        try:
            otdstus = sorted(otdstus, key=lambda i: (i.owner.lname, i.owner.fname))
        except Exception as error:
            flash(f"Sort failed in the roster route with error: {error}")

    return render_template('roster.html', gclassname=gclassroom.gclassdict['name'], gclassid=gclassid, otdstus=otdstus)

@app.route("/getroster/<gclassid>/<index>", methods=['GET','POST'])
@app.route("/getroster/<gclassid>", methods=['GET','POST'])
def getroster(gclassid, index=0):
    index = int(index)

    # Get the Google Classroom from OTData (SQLAlchemy)
    currGClass = GoogleClassroom.query.filter_by(gclassid=gclassid).first()
    if not currGClass:
        flash(f"There is no Google Classroom with the id {gclassid}")
        return redirect(url_for('gclasslist'))

    if google.oauth2.credentials.Credentials(**session['credentials']).valid:
        credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    else:
        return redirect('/authorize')
    session['credentials'] = credentials_to_dict(credentials)
    classroom_service = googleapiclient.discovery.build('classroom', 'v1', credentials=credentials)

    # If the index is 0 then we are at the beginning of the process and need to get the roster from Google
    if index == 0:
        session['missingStus'] = []
        currGClass.grosterTemp = []
        db.session.commit()
        gstudents = []
        pageToken = None
        try:
            students_results = classroom_service.courses().students().list(courseId=gclassid, pageToken=pageToken).execute()
        except RefreshError:
            flash("When I asked for the courses from Google Classroom I found that your credentials needed to be refreshed.")
            return redirect('/authorize')

        while True:
            pageToken = students_results.get('nextPageToken')
            gstudents.extend(students_results['students'])
            if not pageToken:
                break
            students_results = classroom_service.courses().students().list(courseId=gclassid, pageToken=pageToken).execute()

        studentsOnly = []
        for student in gstudents:
            if student['profile']['emailAddress'][:2] == 's_':
                studentsOnly.append(student)
        gstudents = studentsOnly
    else:
        gstudents = currGClass.grosterTemp if currGClass.grosterTemp else []

    numStus = len(gstudents)
    numIterations = 3
    iterator = 0
    errors = []

    for stu in gstudents[index:]:
        try:
            # see if they are in OTData
            otdstu = User.query.filter_by(email_ousd=stu['profile']['emailAddress']).first()
            if otdstu and not otdstu.gid:
                otdstu.gid = stu['profile']['id']
                db.session.commit()
        except Exception as error:
            session['missingStus'].append(f"{stu['profile']['name']['fullName']} had error: {error}")
            otdstu = None

        if not otdstu:
            # Create new student
            newStu = User(
                gid=stu['profile']['id'],
                fname=stu['profile']['name']['givenName'],
                lname=stu['profile']['name']['familyName'],
                email_ousd=stu['profile']['emailAddress'],
                role="Student"
            )
            try:
                db.session.add(newStu)
                db.session.commit()
            except IntegrityError as error:
                db.session.rollback()
                errors.append(f"duplicate--> {newStu.fname} {newStu.lname} {error}")
            else:
                flash(f"NEW--> {newStu.fname} {newStu.lname}")
                enrollment = GEnrollment(
                    owner_id=newStu.id,
                    gclassroom_id=currGClass.id
                )
                try:
                    db.session.add(enrollment)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                otdstu = newStu
        else:
            # Check if enrollment exists
            enrollment = GEnrollment.query.filter_by(owner_id=otdstu.id, gclassroom_id=currGClass.id).first()
            if not enrollment:
                flash(f"NEW --> {index+1}/{numStus}: {stu['profile']['name']['fullName']}")
                enrollment = GEnrollment(
                    owner_id=otdstu.id,
                    gclassroom_id=currGClass.id
                )
                db.session.add(enrollment)
                db.session.commit()
            else:
                flash(f"Existing --> {index+1}/{numStus}: {stu['profile']['name']['fullName']}")

        index = index + 1
        iterator = iterator + 1
        if iterator == numIterations:
            break

    flash(errors)

    if numStus > index:
        # save the progress
        currGClass.grosterTemp = gstudents
        db.session.commit()
        url = f"/getroster/{gclassid}/{index}"
        return render_template('loading.html', url=url, nextIndex=index, total=numStus)

    currGClass.grosterTemp = gstudents
    db.session.commit()
    if 'missingStus' in session:
        for stu in session['missingStus']:
            flash(stu)
        session.pop('missingStus', None)
    return redirect(url_for('roster',gclassid=gclassid))

@app.route('/rostersort/<gclassid>/<sort>', methods=['GET', 'POST'])
@app.route('/rostersort/<gclassid>', methods=['GET', 'POST'])
def editrostersortorder(gclassid, sort=None):
    gclassroom = GoogleClassroom.query.filter_by(gclassid=gclassid).first()
    if not gclassroom:
        flash("Google Classroom not found.")
        return redirect(url_for('checkin'))

    enrollments = GEnrollment.query.filter_by(gclassroom_id=gclassroom.id).all()
    if sort:
        rosterToSort = sorted(enrollments, key=lambda i: (i.sortCohort, i.owner.lname, i.owner.fname))
        groster = rosterToSort
    else:
        groster = enrollments

    sortForms = {}
    form = SortOrderCohortForm()

    if form.validate_on_submit():
        otStudent = User.query.filter_by(email_ousd=form.gmail.data).first()
        if not otStudent:
            flash(Markup(f"You need to <a href='/addgclass/{form.gmail.data}/{gclassid}'>add this student to the class.</a>"))
        else:
            enrollment = GEnrollment.query.filter_by(owner_id=otStudent.id, gclassroom_id=gclassroom.id).first()
            if not enrollment:
                flash(Markup(f"You need to <a href='/addgclass/{form.gmail.data}/{gclassid}'>add {otStudent.fname} {otStudent.lname}</a> to the class."))
            else:
                enrollment.sortCohort = form.sortOrderCohort.data
                db.session.commit()
                enrollments = GEnrollment.query.filter_by(gclassroom_id=gclassroom.id).all()
                groster = sorted(enrollments, key=lambda i: (i.sortCohort, i.owner.lname, i.owner.fname))

    for i, enrollment in enumerate(groster):
        sortOrderCohort = getattr(enrollment, 'sortCohort', None)
        sortForms['form'+str(i)] = SortOrderCohortForm()
        sortForms['form'+str(i)].gid.data = enrollment.owner.id
        sortForms['form'+str(i)].gmail.data = enrollment.owner.email_ousd
        sortForms['form'+str(i)].gclassid.data = enrollment.gclassroom.id
        sortForms['form'+str(i)].sortOrderCohort.data = sortOrderCohort
        if gclassroom.sortcohorts:
            choices = [(choice, choice) for choice in gclassroom.sortcohorts]
            sortForms['form'+str(i)].sortOrderCohort.choices = choices
        sortForms['form'+str(i)].order.data = i

    numForms = len(sortForms)

    return render_template('rostersortform.html.j2', gclassroom=gclassroom, forms=sortForms, numForms=numForms, groster=groster)

@app.route('/sortcohorts/<gcid>', methods=['GET','POST'])
def sortcohorts(gcid):
    googleClassroom = GoogleClassroom.query.filter_by(gclassid=gcid).first()
    if not googleClassroom:
        flash("Google Classroom not found.")
        return redirect(url_for('gclasslist'))

    form = SimpleForm()

    if form.validate_on_submit():
        cohorts = form.field.data
        sortCohorts = [c.strip() for c in cohorts.split(',')]
        googleClassroom.sortcohorts = sortCohorts
        db.session.commit()
        return redirect(url_for('editrostersortorder', gclassid=gcid))

    if googleClassroom.sortcohorts:
        form.field.data = ','.join(googleClassroom.sortcohorts)

    return render_template('sortcohorts.html', form=form, googleClassroom=googleClassroom)
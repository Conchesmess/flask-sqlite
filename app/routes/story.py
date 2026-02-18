
# This file handles the "story" features in the app.
# Users can create, view, edit, and delete stories.

from app import app, db, confirm_delete  # Import app, database, and delete helper
from app.classes.data import Story  # Story model
from app.classes.forms import StoryForm  # Form for stories
from datetime import datetime, timezone  # For dates and times
from flask import redirect, flash, session, url_for, render_template  # Flask tools
from flask_login import current_user, login_required  # Login tools

# Show all stories
@app.route('/story/list')
def stories():
    stories = Story.query.order_by(Story.createdate.desc()).all()
    if stories:
        render_template("stories.html",stories=stories)
        return render_template("stories.html",stories=stories)
    else:
        flash("no stories", "info")
        return redirect(url_for("index"))

# Create a new story
@app.route('/story/new', methods=['GET', 'POST'])
def newStory():
    form = StoryForm()
    if form.validate_on_submit():
        newStory = Story(
                title=form.title.data,
                content=form.content.data,
                author_id = current_user.id
            )
        db.session.add(newStory)
        db.session.commit()
        return redirect(url_for("story",id=newStory.id))
    return render_template("story_form.html", form=form)

# View a single story
@app.route('/story/<int:id>')
def story(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    return render_template("story.html",story=thisStory)

# Edit a story
@app.route('/story/edit/<int:id>', methods=['GET', 'POST'])
def editStory(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    form = StoryForm()
    if form.validate_on_submit():
        thisStory.title = form.title.data
        thisStory.content = form.content.data
        db.session.commit()
        return redirect(url_for('story',id=id))
    form.title.data = thisStory.title
    form.content.process_data(thisStory.content)
    return render_template('story_form.html',form=form)

# Delete a story
@app.route('/story/delete/<int:id>', methods=['GET', 'POST'])
@confirm_delete(Story, redirect_url='/story/list', message_fields=['title','author','content'], message_date_field = 'createdate')
def deleteStory(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    db.session.delete(thisStory)
    db.session.commit()
    return redirect(url_for("stories"))
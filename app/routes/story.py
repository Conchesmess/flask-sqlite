from app import app, db, confirm_delete
from app.classes.data import Story
from app.classes.forms import StoryForm
from datetime import datetime, timezone
from flask import redirect, flash, session, url_for, render_template
from flask_login import current_user, login_required

@app.route('/story/list')
def stories():
    stories = Story.query.order_by(Story.createdate.desc()).all()
    if stories:
        render_template("stories.html",stories=stories)
        return render_template("stories.html",stories=stories)
    else:
        flash("no stories", "info")
        return redirect(url_for("index"))


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


@app.route('/story/<int:id>')
def story(id):
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))
    return render_template("story.html",story=thisStory)

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


@app.route('/story/delete/<int:id>', methods=['GET', 'POST'])
@confirm_delete(Story, redirect_url='/story/list', message_fields=['title','author','content'], message_date_field = 'createdate')
def deleteStory(id):
    
    thisStory = db.one_or_404(db.select(Story).filter_by(id=id))

    db.session.delete(thisStory)
    db.session.commit()

    return redirect(url_for("stories"))
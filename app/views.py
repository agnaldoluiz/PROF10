from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_oauth import OAuth
from app import app, facebook, db, models, lm
from forms import ProfessorForm, PostForm, CollegeForm, SearchForm
from models import User, ROLE_USER, ROLE_ADMIN, Professor, Post, College

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
        title = 'Home')

# --- LOGIN ---

@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    user = User.query.filter_by(email=me.data['email']).first()

    if user is not None and me.data['email'] == user.email:
        login_user(user)
        flash('Logged in Successfully!')
        return redirect(url_for('main'))

    user = User(first_name = me.data['first_name'], last_name = me.data['last_name'],
        email = me.data['email'], role = ROLE_USER)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    flash('User registered!')
    return redirect(url_for('main'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('index'))

#---- Other functions ------

@app.route('/main')
def main():
    return render_template('main.html',
        title = 'Main',
        posts = Post.query.all())

@app.route('/about')
def about():
    return render_template("about.html",
        title = 'About')

@app.route('/contact')
def contact():
    return render_template("contact.html",
        title = 'Contact')

@app.route('/areyouaprof')
def areyouaprof():
    return render_template("areyouaprof.html",
        title = 'Are you a Prof?')

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    form = ProfessorForm()
    form2 = CollegeForm()

    if form.add_professor.data and form.validate_on_submit():
        professor = Professor(first_name = form.first_name.data, last_name = form.last_name.data, department = form.department.data, college = College.query.filter_by(college_acronym = form.college.data).first())
        db.session.add(professor)
        db.session.commit()
        flash('Professor Added')
        return redirect(url_for('professor', profname = professor.first_name))

    if form2.add_college.data and form2.validate_on_submit():
        college = College(college_name = form2.college_name.data, college_acronym = form2.college_acronym.data, state = form2.state.data)
        db.session.add(college)
        db.session.commit()
        flash('College Added')
        return redirect(url_for('main'))

    return render_template("admin.html",
        form = form,
        form2 = form2,
        title = 'Admin')

@app.route('/professors')
def professors():
    professors = Professor.query.all()

    return render_template('professors.html',
        professors = professors)

@app.route('/professor/<profname>', methods = ['GET', 'POST'])
def professor(profname):
    professor = Professor.query.filter_by(first_name = profname).first()
    if professor == None:
        flash('Professor' + profname + 'not found.')
        return redirect(url_for('main'))

    form = PostForm()

    if form.validate_on_submit():
        rating = (float(form.teaching.data) + float(form.material.data) + float(form.participation.data))/3
        attendance = ''
        if int(form.attendance.data):
            attendance = 'Mandatory'
        else:
            attendance = 'Non-mandatory'
        professor = Professor.query.filter_by(first_name = profname).first()
        post = Post(body = form.post.data, subject = form.subject.data, attendance = attendance, teaching = form.teaching.data, material = form.material.data, participation = form.participation.data, difficulty = form.difficulty.data, rating = rating, author = g.user, about = professor)
        db.session.add(post)
        if professor.rating is None:
            professor.rating = rating
        else:
            professor.rating = (rating + professor.rating*len(professor.posts.all()))/(1+len(professor.posts.all()))
        db.session.commit()
        flash('Post Posted!')
        return redirect(url_for('professor', profname=profname))

    return render_template('professor.html',
        professor = professor,
        form = form,
        posts = Professor.query.filter_by(first_name = profname).first().posts.all())

@app.route('/colleges')
def colleges():
    colleges = College.query.all()
    

    return render_template('colleges.html',
        colleges = colleges)

@app.route('/college/<college_name>')
def college(college_name):
    college = College.query.filter_by(college_name = college_name).first()
    professors = college.professors.all()
    summ = 0
    for professor in professors:
        try:
            summ = summ + float(professor.rating)
        except TypeError:
            break
    try:
        average = summ/len(professors)
    except ZeroDivisionError:
        average = 0

    return render_template('college.html',
        college = college,
        professors = professors,
        average = average)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

from config import MAX_SEARCH_RESULTS

@app.route('/search_results/<query>')
def search_results(query):
    results = Professor.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('main'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('main'))

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

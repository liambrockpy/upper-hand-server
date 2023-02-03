from app import app, db
from flask import jsonify, render_template, flash, redirect, url_for
from werkzeug import exceptions
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, login_required
from app.models import User

search_term = "" 

@app.route("/")
def index():
    return render_template('index.html')


# @app.route("/search", methods=['GET', 'POST'])
# def search():
#     birds = []
#     form = SearchBirdsForm()
#     favourite = EmptyForm()
#     if form.validate_on_submit():
#         flash(f'Searching {form.bird.data}...')
#         global search_term
#         search_term = form.bird
#         return redirect(url_for('search'))
#     if search_term:
#         birds = Bird.query.filter(Bird.name == search_term)
#         search_term = ""
#     else:
#         birds = Bird.query.all()
#     return render_template('search.html', birds=birds, form=form, favourite=favourite)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


# @app.route('/favourite/<bird_name>', methods=['POST'])
# @login_required
# def favourite(bird_name):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         bird = Bird.query.filter_by(name=bird_name).first()
#         if bird is None:
#             flash('Bird {} not found.'.format(bird_name))
#             return redirect(url_for('search'))
#         current_user.favourite(bird)
#         db.session.commit()
#         flash('You added {} to your list of favourites!'.format(bird_name))
#         return redirect(url_for('search'))
#     else:
#         return redirect(url_for('search'))


# @app.route('/unfavourite/<bird_name>', methods=['POST'])
# @login_required
# def unfavourite(bird_name):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         bird = Bird.query.filter_by(name=bird_name).first()
#         if bird is None:
#             flash('Bird {} not found.'.format(bird_name))
#             return redirect(url_for('search'))
#         current_user.unfavourite(bird)
#         db.session.commit()
#         flash('You removed {} from your favourites.'.format(bird_name))
#         url = request.referrer
#         if 'birds' in url:
#             return redirect(url_for('birds'))
#         elif 'search' in url:
#             return redirect(url_for('search'))
#     else:
#         return redirect(url_for('birds'))


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm()

#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('index')
#         return redirect(next_page)

#     return render_template('login.html', title='Sign In', form=form)

# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

##########################

@app.errorhandler(exceptions.NotFound)
def error_404(err):
    return jsonify({"message": f"Oops.. {err}"}), 404

@app.errorhandler(exceptions.BadRequest)
def handle_400(err):
    return {'message': f'Oops! {err}'}, 400

@app.errorhandler(exceptions.InternalServerError)
def handle_500(err):
    return {'message': f"It's not you, it's us"}, 500

if __name__ == "__main__":
    app.run(debug=True)

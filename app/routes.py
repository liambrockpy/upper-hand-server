from app import app, db
from app.sockets import socketio
from flask import jsonify, request, session
from werkzeug import exceptions
from werkzeug.urls import url_parse
from app.models import User, Deck
from flask_socketio import SocketIO, emit

from poker import Card
from poker.hand import Hand, Combo

from pokerlib.enums import Rank, Suit
from pokerlib import HandParser


@app.route('/')
def index():
    # deck1 = Deck()
    # deck2 = Deck()
    # print("FIRST",deck1.deck)
    # print("SECOND",deck2.deck)
    # print(list(Combo))
    return 'Hello World'


@app.route('/@me')
def get_current_user():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.filter_by(id=user_id).first()
    return jsonify({'id': user.id, 'email': user.email})
 

@app.route("/register", methods=['POST'])
def register():
    email = request.json['email']
    password = request.json['password']

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({'error': 'User already exists'}), 409

    new_user = User(email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({'id': new_user.id, 'email': new_user.email})


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first() 

    if user is None or not user.check_password(password):
        return jsonify({'error': 'Unauthorized'}), 401

    session['user_id'] = user.id

    return jsonify({'id': user.id, 'email': user.email})


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id')
    return "200"


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
    socketio.run(app)

from app import app, db
from app.sockets import socketio

from flask import jsonify, render_template, flash, redirect, url_for
from werkzeug import exceptions
from werkzeug.urls import url_parse
from app.models import User
from flask_socketio import SocketIO, emit

search_term = "" 

@app.route("/")
def index():
    return render_template('index.html')

# @socketio.on('connect')
# def connect():
#     print('Client connected')

# @socketio.on('disconnect')
# def disconnect():
#     print('Client disconnected')

# @socketio.on('message')
# def handle_message(message):
#     emit('message', message, broadcast=True)


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

from flask_socketio import SocketIO, emit
from app import app, db, socketio

@socketio.on('connect')
def connect():
    print('Client connected')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    emit('message', message, broadcast=True)

from flask_socketio import SocketIO, emit
from app import app, db, socketio
from app.models import Player, GameState, Deck

@socketio.on('connect')
def connect():
    print('Client connected')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    emit('message', message, broadcast=True)

@socketio.on('create_game')
def create_game(game_data, player_data):
    host = Player(is_host=True, name=player_data['name'])
    game = GameState(join_code=game_data['join_code'], deck= Deck.deck, phase="preflop", starting_chips=game_data['starting_chips'], small_blind_amount=game_data['small_blind'], big_blind_amount=game_data['big_blind'], players=[host], community_cards=[], total_chips_in_play=0, winner='')
    

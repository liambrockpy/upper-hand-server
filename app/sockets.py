from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app, db, socketio
from app.models import Player, GameState

games = []

@socketio.on('connect')
def connect():
    print(f'Client connected {request.sid}')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(message):
    emit('message', message, broadcast=True)

@socketio.on('create_game')
def create_game(game_data, player_data):
    host = Player(is_host=True, name=player_data['name'], avatar = player_data['avatar'], remaining_chips=game_data['starting_chips'])
    game = GameState(join_code=game_data['join_code'], host=host)
    games.append(game)
    join_room(game.join_code)
    emit("create_game_response", game, host)

@socketio.on('join_game')
def join_game(join_code, player_data):
    game = next((game for game in games if game["join_code"] == join_code), None)
    if game == None:
        emit('wrong_join_code')
    else:
        player = Player(is_host=False, name=player_data['name'], avatar=player_data['avatar'])
        game.add_player(player)
        join_room(join_code)
        emit("joined_game", game, player, room=join_code)

@socketio.on('leave-game')
def leave_game(join_code, player):
    game = next((game for game in games if game["join_code"] == join_code), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.remove_player(player)
        leave_room(join_code)
        emit("left_game", game, room=join_code)

@socketio.on('start-game')
def start_game(game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.starting_chips = game_data["starting_chips"]
        game.small_blind_amount = game_data["small_blind_amount"]
        game.big_blind_amount = game_data["big_blind_amount"]
        emit("starting-game", game, room=game_data["join_code"])    

    
@socketio.on('update_player')
def update_player(player_data, game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.update_player(player_data)
        emit("Update_Player_Response", game)
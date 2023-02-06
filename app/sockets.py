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

# @socketio.on('join')
# def on_join(data):
#     # username = session['username']
#     room = data['room']
#     join_room(room)
#     send(username + ' has entered the room.', to=room)

@socketio.on('send-new-room')
def admin_join_room(join_code):
    join_room(join_code)
    return


@socketio.on('create_game')
def create_game(game_data, player_data):
    host = Player(
        is_host=True, 
        name=player_data['name'], 
        avatar = player_data['avatar'], 
        remaining_chips=game_data['starting_chips']
    )
    game = GameState(
        join_code=game_data['join_code'], 
        starting_chips=game_data['starting_chips'], 
        small_blind_amount=game_data['small_blind'], 
        big_blind_amount=game_data['big_blind'], 
        host=host.__dict__
    )
    games.append(game)
    # join_room(game['join_code'])
    return game
    # emit("create_game_response", game, host)

@socketio.on('join_game')
def join_game(player_data):
    join_code = player_data["join_code"]
    game = next((game for game in games if game["join_code"] == join_code), None)
    if game == None:
        emit('wrong_join_code')
    else:
        player = Player(is_host=False, name=player_data['name'], avatar=player_data['avatar'])
        game.add_player(player)
        join_room(join_code)
        emit("joined_game", game, player, room=join_code)

@socketio.on('leave_game')
def leave_game(player):
    join_code = player["join_code"]
    game = next((game for game in games if game["join_code"] == join_code), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.remove_player(player)
        leave_room(join_code)
        emit("left_game", game, room=join_code)

@socketio.on('start_game')
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
def update_player(player_data):
    game = next((game for game in games if game["join_code"] == player_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.update_player(player_data)
        emit("Update_Player_Response", game, room=player_data["join_code"])


@socketio.on('player_betting_action')
def player_betting_action(bet_type, bet_amount, player):
    game = next((game for game in games if game["join_code"] == player["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        if bet_type == "fold":
            game.fold(player.id)
        else:
            game.bet(player.id, bet_amount, bet_type)
        emit("player_action_response", game, room=player["join_code"])

@socketio.on('flop')
def flop(game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.deal_flop()
        game.reset_bets()
        emit("flop_response", game, room=game_data["join_code"])

@socketio.on('turn')
def turn(game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.deal_turn()
        game.reset_bets()
        emit("turn_response", game, room=game_data["join_code"])

@socketio.on('river')
def river(game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.deal_river()
        game.reset_bets()
        emit("river_response", game, room=game_data["join_code"])

@socketio.on('showdown')
def showdown(game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.showdown()
        emit("showdown_response", game, room=game_data["join_code"])

@socketio.io('start_round')
def start_round(game_data):
    game = next((game for game in games if game["join_code"] == game_data["join_code"]), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.start_round()
        emit("end_round_response", game, room=game_data["join_code"])

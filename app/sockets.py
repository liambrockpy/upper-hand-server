from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app, db, socketio
from app.models import Player, GameState
import random
import json 

games = []

def find_game_by_rid(room_id):
    for g in games:
        rid = g.get_join_code()
        if str(rid) == str(room_id):
            return g
    return None

# ROUTE FUNCTIONS

def create_game(player_data):
    hash = random.randrange(1000, 9999)
    host = Player(
        id=player_data['id'],
        is_host=True,
        join_code=hash, 
        name=player_data['email'].split('@')[0],
        avatar = player_data['avatar'], 
    )
    game = GameState(
        join_code=hash, 
        host=host
    )
    games.append(game)
    return game

def join_game(room_id, player_data):
    game = find_game_by_rid(room_id)
    if game == None:
        return None
    else:
        player = Player(is_host=False, id=player_data['id'], name=player_data['email'].split('@')[0], join_code=room_id, avatar=player_data['avatar'])
        game.add_player(player)
        return game
        
def start_game(room_id, start_c, small_b, big_b):
    game = find_game_by_rid(room_id)
    if game == None:
        return None
    # else:
        # game['starting_chips'] = start_c
        # game['small_blind_amount'] = start_c
        # game['big_blind_amount'] = start_c


# SOCKET FUNCTIONS

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

@socketio.on('player_join_room')
def player_join_room(room_code):
    # print(type(room_code))
    # print(obj)
    # room_code = obj[0]
    # print(room_code, "ADADADADADADADADADADADADADADADADDADA")
    join_room(room_code)
    game = find_game_by_rid(room_code)
    json_res = json.dumps(game, default=lambda obj: obj.__dict__)
    emit("joined_game", json_res, room=room_code)


@socketio.on('leave_game')
def leave_game(player_id, room_id):
    # print(f'player from leave_game: ', player)
    r_id = int(room_id)
    game = find_game_by_rid(r_id)
    if game == None:
        emit('wrong_join_code')
    else:
        game.remove_player(player_id)
        leave_room(r_id)
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("left_game", json_res, room=r_id)

# @socketio.on('start_game')
# def start_game(game_data):
#     game = find_game_by_rid(game_data["join_code"])
#     rid = int(game_data["join_code"])
#     if game == None:
#         emit('wrong_join_code')
#     else:
#         game.active = True
#         json_res = json.dumps(game, default=lambda obj: obj.__dict__)
#         emit("starting_game", json_res, room=rid)    

    
@socketio.on('update_player')
def update_player(obj):
    game = find_game_by_rid(obj["join_code"])
    if game == None:
        emit('wrong_join_code')
    else:
        seat = game.get_player_by_id(obj["id"])
        game.players[seat].name = obj["name"]
        game.players[seat].avatar = obj["avatar"]
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("update_player_response", json_res, room=obj["join_code"])


# def update_player(player_data):
#     game = find_game_by_rid(player_data["join_code"])
#     if game == None:
#         emit('wrong_join_code')
#     else:
#         game.update_player(player_data)
#         json_res = json.dumps(game, default=lambda obj: obj.__dict__)
#         emit("update_player_response", json_res, room=player_data["join_code"])



@socketio.on('update_game_settings')
def update_game_settings(obj):
    print(obj["room_code"])
    game = find_game_by_rid(obj["room_code"])
    if game == None:
        emit('wrong_join_code')
    else:
        game.starting_chips = obj["startingChips"]
        game.small_blind_amount = obj["smallBlind"]
        game.big_blind_amount = obj["bigBlind"]
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("update_game_settings_response", json_res, room=obj["room_code"])

@socketio.on('player_betting_action')
def player_betting_action(obj):
    game = find_game_by_rid(obj["join_code"])
    print(obj)
    if game == None:
        emit('wrong_join_code')
    else:
        if obj.bet_type == "fold":
            game.fold(obj["id"])
        else:
            game.bet(obj["id"], obj["bet_amount"], obj["bet_type"])
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("player_betting_action_response", json_res, room=obj["join_code"])

@socketio.on('flop')
def flop(game_data):
    game = find_game_by_rid(game_data["join_code"])
    if game == None:
        emit('wrong_join_code')
    else:
        game.deal_flop()
        game.reset_bets()
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("flop_response", json_res, room=game_data["join_code"])

@socketio.on('turn')
def turn(game_data):
    game = find_game_by_rid(game_data["join_code"])
    if game == None:
        emit('wrong_join_code')
    else:
        game.deal_turn()
        game.reset_bets()
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("turn_response", json_res, room=game_data["join_code"])

@socketio.on('river')
def river(game_data):
    game = find_game_by_rid(game_data["join_code"])
    if game == None:
        emit('wrong_join_code')
    else:
        game.deal_river()
        game.reset_bets()
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("river_response", json_res, room=game_data["join_code"])

@socketio.on('showdown')
def showdown(game_data):
    game = find_game_by_rid(game_data["join_code"])
    if game == None:
        emit('wrong_join_code')
    else:
        game.showdown()
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        emit("showdown_response", json_res, room=game_data["join_code"])

@socketio.on('start_round')
def start_round(game_data):
    print("start_round")
    game = find_game_by_rid(game_data['join_code'])
    if game == None:
        emit('wrong_join_code')
    else:
        game.active = True
        game.start_round()
        json_res = json.dumps(game, default=lambda obj: obj.__dict__)
        print(json_res)
        emit("start_round_response", json_res, room=game_data["join_code"])


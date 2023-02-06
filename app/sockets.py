from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app, db, socketio
from app.models import Player, GameState

games = []

@socketio.on('connect')
def connect():
    print('Client connected')

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
def join_game(join_code, player_data):
    game = next((game for game in games if game["join_code"] == join_code), None)
    if game == None:
        emit('wrong_join_code')
    else:
        player = Player(is_host=False, name=player_data['name'], avatar=player_data['avatar'])
        game.add_player(player)
        join_room(join_code)
        emit("joined_game", game, player)

@socketio.on('leave-game')
def leave_game(join_code, player):
    game = next((game for game in games if game["join_code"] == join_code), None)
    if game == None:
        emit('wrong_join_code')
    else:
        game.remove_player(player)
        leave_room(join_code)
        emit("left_game", game)

# @socketio.on('start-game')

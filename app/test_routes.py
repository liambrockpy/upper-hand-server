import json
from app import app, socketio

join_code = ''

# testing basic index route
def test_index(api):
    res = api.get('/')
    assert res.status == '200 OK'
    assert res.data == b"Hello World"

# testing create room
def test_create_new_room(api):
    test_data = {
    "player_data":{
        "id": 1,
        "email": "test@test.com",
        "avatar": "url_1"
    }
    }

    res = api.post('/room', json=test_data, headers={'content-type': 'application/json'})
    res_data = json.loads(res.get_json())
    # print(res_data['players']['seat_1']['name'])#
    global join_code
    join_code=res_data['join_code']

    assert res.status_code == 200
    assert res_data['players']['seat_1']['id'] == 1
    assert res_data['players']['seat_1']['name'] == "test"
    assert res_data['players']['seat_1']['avatar'] == "url_1"
    assert res_data['players']['seat_1']['is_host'] == True
    assert res_data['join_code'] != None


# testing joining a room
def test_join_room(api):
    test_data = {
    "player_data":{
        "id": 2,
        "email": "test1@test.com",
        "avatar": "url_2"
    }
    }

    res = api.post(f'/room/{join_code}', json=test_data, headers={'content-type': 'application/json'})
    res_data = json.loads(res.get_json())
    assert res.status_code == 200
    assert len(res_data['players']) == 8
    assert res_data['players']['seat_2']['id'] == 2
    assert res_data['players']['seat_2']['name'] == "test1"
    assert res_data['players']['seat_2']['avatar'] == "url_2"
    assert res_data['players']['seat_2']['is_host'] == False
    assert res_data['join_code'] == join_code

# testing errors
def test_error_404(api):
    res = api.get('/none')
    assert res.status_code == 404

def test_error_400(api):
    res = api.post('/room', data={"random": "nonsense"})
    data = res.get_json()
    assert res.status_code == 400
    assert data['message'] == 'Oops! 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.'

def test_error_500(api):
    res = api.post('/room', json={"random": "nonsense"})
    data = res.get_json()
    assert res.status_code == 500
    assert data['message'] == "It's not you, it's us"

# test socketio connection
def test_socketio(api):
    socketio_test_client = socketio.test_client(app, flask_test_client=api)
    assert socketio_test_client.is_connected()

# test join room event
def test_socketio_join_room(api):
    socketio_test_client = socketio.test_client(app, flask_test_client=api)
    socketio_test_client.emit("player_join_room", join_code)
    r = socketio_test_client.get_received()
    data = json.loads(r[0]["args"][0])
    assert data["join_code"] == join_code
    assert data != None

# test leave room event
def test_socketio_leave_room(api):
    socketio_test_client = socketio.test_client(app, flask_test_client=api)
    socketio_test_client.emit("player_join_room", join_code)
    socketio_test_client.emit("leave_game", 2, join_code)
    r = socketio_test_client.get_received()
    data = json.loads(r[0]["args"][0])
    assert data["join_code"] == join_code
    assert data != None

# test update player
def test_socketio_update_player(api):
    updateTest = {
        "id": 1,
        "name": "new name",
        "avatar": "new url",
        "join_code": join_code
    }
    socketio_test_client = socketio.test_client(app, flask_test_client=api)
    socketio_test_client.emit("player_join_room", join_code)
    socketio_test_client.emit("update_player", updateTest)
    r = socketio_test_client.get_received()
    data = json.loads(r[0]["args"][0])
    assert data["join_code"] == join_code
    assert data != None

# test update game settings
def test_socketio_update_game(api):
    updateGame = {
        "startingChips": 1,
        "smallBlind": 20,
        "bigBlind": 40,
        "room_code": join_code
    }
    socketio_test_client = socketio.test_client(app, flask_test_client=api)
    socketio_test_client.emit("player_join_room", join_code)
    socketio_test_client.emit("update_game_settings", updateGame)
    r = socketio_test_client.get_received()
    data = json.loads(r[0]["args"][0])
    assert data["join_code"] == join_code
    assert data != None

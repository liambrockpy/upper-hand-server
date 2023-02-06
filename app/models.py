from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from uuid import uuid4
from pokerlib.enums import Rank, Suit
from pokerlib import HandParser
import random

def get_uuid():
    return uuid4().hex

class User(db.Model):
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class GameState:
    def __init__(self, join_code, host):
        self.join_code = join_code
        self.deck = Deck().deck
        self.phase = "preflop"
        self.starting_chips = 10000
        self.small_blind_amount = 20
        self.big_blind_amount = 50
        self.players = {
            "seat_1": host,
            "seat_2": None,
            "seat_3": None,
            "seat_4": None,
            "seat_5": None,
            "seat_6": None,
            "seat_7": None,
            "seat_8": None
        }
        self.community_cards = []
        self.total_chips_in_play = 0
        self.winner = ""
        self.button = "seat_1"

    def get_player_by_id(self, id):
        for seat in self.players:
            if self.players[seat] != None and self.players[seat].id == id:
                return seat

    def add_player(self, player):
        player.remaining_chips = self.starting_chips
        for seat in self.players:
            if self.players[seat] == None:
                self.players[seat] = player
                return seat

    def remove_player(self, player):
        for seat in self.players:
            if self.players[seat] == player:
                self.players[seat] = None
                return seat

    def update_player(self, player):
        for seat in self.players:
            if self.players[seat] != None and self.players[seat].id == id:
                self.players[seat] = player
                return
    
    def button_change(self):
        filled_seats = []
        for seat in self.players:
            if self.players[seat] != None:
                filled_seats.append(seat)

        filled_len = len(filled_seats)
                
        for seat in filled_seats:
            if seat == self.button:
                # assigning button role in the GameState
                self.button = filled_seats[(filled_seats.index(seat) + 1) % filled_len]

        # assigning roles in player states        
        self.players[self.button].role = "button"
        self.players[(filled_seats.index(self.button) + 1) % filled_len].role = "small_blind"
        self.players[(filled_seats.index(self.button) + 2) % filled_len].role = "big_blind"
        self.players[(filled_seats.index(self.button) + 3) % filled_len].role = "preflop_starter"

    def start_round(self):
        # reset player states
        for seat in self.players:
            if self.players[seat] != None:
                self.players[seat].current_bet = 0
                self.players[seat].bet_type = None
                self.players[seat].is_playing = True
                self.players[seat].role = None
                self.players[seat].hand = None
                # self.players[seat].remaining_chips = self.players[seat].original_chips
                self.players[seat].chips_in_play = 0

        # reset game state
        self.community_cards = []
        self.total_chips_in_play = 0
        self.winner = None
        self.deck = Deck().deck
        self.phase = "preflop"

        # deal cards
        for seat in self.players:
            if self.players[seat] != None:
                self.players[seat].hand = [self.deck.pop(), self.deck.pop()]

        # assign roles
        self.button_change()

    def deal_flop(self):
        self.community_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        self.phase = "flop"

    def deal_turn(self):
        self.community_cards.append(self.deck.pop())
        self.phase = "turn"

    def deal_river(self):
        self.community_cards.append(self.deck.pop())
        self.phase = "river"

    def showdown(self):
        self.phase = "showdown"
        self.winner = self.get_winner()


    def get_winner(self):
        # get all players still in the game
        players_in_game = []
        for seat in self.players:
            if self.players[seat] != None and self.players[seat].is_playing == True:
                players_in_game.append(self.players[seat])

        # user case where everyone has folded except one player
        index = 1
        tries = 0
        while(len(players_in_game) > 1):
            hand1 = players_in_game[0].hand + self.community_cards
            hand2 = players_in_game[index % len(players_in_game)].hand + self.community_cards
            hand1.parse()
            hand2.parse()
            if hand1 == hand2:
                index += 1
            elif hand1 > hand2:
                seat = self.get_player_by_id(players_in_game[index % len(players_in_game)].id)
                self.update_loser(seat)
                players_in_game.pop(index % len(players_in_game))
            else:
                seat = self.get_player_by_id(players_in_game[0].id)
                self.update_loser(seat)
                players_in_game.pop(0)
                index = 1
            tries += 1
            if tries > 30:
                break
        
        # One winner
        if len(players_in_game) == 1:
            self.winner = players_in_game[0].name
            seat = self.get_player_by_id(players_in_game[0].id)
            self.players[seat].remaining_chips += self.total_chips_in_play
            self.players[seat].is_playing = False
            return
        # Multiple Winners
        else:
            # split the pot
            self.winner = ""
            for player in players_in_game:
                self.winner += player.name + " "
                seat = self.get_player_by_id(player.id)
                self.players[seat].remaining_chips += self.total_chips_in_play / len(players_in_game)
                self.players[seat].is_playing = False
            return
        
    def update_loser(self, seat):
        self.players[seat].is_playing = False
        self.players[seat].remaining_chips -= self.players[seat].chips_in_play

    def fold(self, id):
        seat = self.get_player_by_id(id)
        self.players[seat].is_playing = False
        self.players[seat].bet_type = "fold"
    
    def bet(self, id, amount, type):
        seat = self.get_player_by_id(id)
        self.players[seat].remaining_chips -= amount
        self.players[seat].chips_in_play += amount
        self.players[seat].current_bet += amount
        self.total_chips_in_play += amount
        self.players[seat].bet_type = type

    def reset_bets(self):
        for seat in self.players:
            if self.players[seat] != None:
                self.players[seat].current_bet = 0
                self.players[seat].bet_type = None




class Player:
    def __init__(self, join_code, name, avatar, is_host, remaining_chips):
        self.id = get_uuid()
        self.join_code = join_code
        self.name = name
        self.avatar = avatar
        self.is_host = is_host
        # self.original_chips = original_chips
        self.remaining_chips = remaining_chips
        self.chips_in_play = 0
        self.current_bet = 0
        self.bet_type = None
        self.is_playing = False
        self.role = None
        self.hand = None

class Deck:
    def __init__(self):
        deck = [
            (Rank.TWO, Suit.CLUB), (Rank.TWO, Suit.DIAMOND), (Rank.TWO, Suit.HEART), (Rank.TWO, Suit.SPADE),
            (Rank.THREE, Suit.CLUB), (Rank.THREE, Suit.DIAMOND), (Rank.THREE, Suit.HEART), (Rank.THREE, Suit.SPADE),
            (Rank.FOUR, Suit.CLUB), (Rank.FOUR, Suit.DIAMOND), (Rank.FOUR, Suit.HEART), (Rank.FOUR, Suit.SPADE),
            (Rank.FIVE, Suit.CLUB), (Rank.FIVE, Suit.DIAMOND), (Rank.FIVE, Suit.HEART), (Rank.FIVE, Suit.SPADE),
            (Rank.SIX, Suit.CLUB), (Rank.SIX, Suit.DIAMOND), (Rank.SIX, Suit.HEART), (Rank.SIX, Suit.SPADE),
            (Rank.SEVEN, Suit.CLUB), (Rank.SEVEN, Suit.DIAMOND), (Rank.SEVEN, Suit.HEART), (Rank.SEVEN, Suit.SPADE),
            (Rank.EIGHT, Suit.CLUB), (Rank.EIGHT, Suit.DIAMOND), (Rank.EIGHT, Suit.HEART), (Rank.EIGHT, Suit.SPADE),
            (Rank.NINE, Suit.CLUB), (Rank.NINE, Suit.DIAMOND), (Rank.NINE, Suit.HEART), (Rank.NINE, Suit.SPADE),
            (Rank.TEN, Suit.CLUB), (Rank.TEN, Suit.DIAMOND), (Rank.TEN, Suit.HEART), (Rank.TEN, Suit.SPADE),
            (Rank.JACK, Suit.CLUB), (Rank.JACK, Suit.DIAMOND), (Rank.JACK, Suit.HEART), (Rank.JACK, Suit.SPADE),
            (Rank.QUEEN, Suit.CLUB), (Rank.QUEEN, Suit.DIAMOND), (Rank.QUEEN, Suit.HEART), (Rank.QUEEN, Suit.SPADE),
            (Rank.KING, Suit.CLUB), (Rank.KING, Suit.DIAMOND), (Rank.KING, Suit.HEART), (Rank.KING, Suit.SPADE),
            (Rank.ACE, Suit.CLUB), (Rank.ACE, Suit.DIAMOND), (Rank.ACE, Suit.HEART), (Rank.ACE, Suit.SPADE)
        ]
        random.shuffle(deck)
        self.deck = deck

        # def get_deck_data():
        #     return deck

    

    
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
    def __init__(self, join_code, deck, phase, starting_chips, small_blind_amount, big_blind_amount, host, community_cards, total_chips_in_play, winner):
        self.join_code = join_code
        self.deck = deck
        self.phase = phase
        self.starting_chips = starting_chips
        self.small_blind_amount = small_blind_amount
        self.big_blind_amount = big_blind_amount
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
        self.community_cards = community_cards
        self.total_chips_in_play = total_chips_in_play
        self.winner = winner

    def add_player(self, player):
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
            if self.players[seat].name == player.name:
                self.players[seat] = player
                return seat


class Player:
    def __init__(self, name, avatar, is_host, original_chips, remaining_chips, chips_in_play, current_bet, bet_type, is_playing, role, hand):
        self.name = name
        self.avatar = avatar
        self.is_host = is_host
        self.original_chips = original_chips
        self.remaining_chips = remaining_chips
        self.chips_in_play = chips_in_play
        self.current_bet = current_bet
        self.bet_type = bet_type
        self.is_playing = is_playing
        self.role = role
        self.hand = hand

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
    

    
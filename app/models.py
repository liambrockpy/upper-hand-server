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
        self.winner = []
        self.active = False
        self.button = "seat_1"
        self.highest_bet = 0
        self.betting_player_id = None
        self.betting_player_seat = None
        self.betting_over = False
        self.num_players = len(self.get_filled_seats())
        self.round_num = 0
        self.start_point = None
        self.round_over = False
        self.is_everyone_allin = False

    def __getitem__(self, index):
        return self

    def get_join_code(self):
        return self.join_code

    def get_player_by_id(self, id):
        for seat in self.players:
            if self.players[seat] != None and self.players[seat].id == id:
                return seat

    def add_player(self, player):
        player.remaining_chips = self.starting_chips
        for seat in self.players:
            if self.players[seat] == None:
                self.players[seat] = player
                self.num_players = len(self.get_filled_seats())
                return seat

    def remove_player(self, player_id):
        for seat, p in self.players.items():
            if p.id == player_id:
                self.players[seat] = None
                self.num_players = len(self.get_filled_seats())
                return seat

    def update_player(self, player):
        for seat in self.players:
            if self.players[seat] != None and self.players[seat].id == id:
                self.players[seat] = player
                return

    def get_filled_seats(self):
        filled_seats = []
        for seat in self.players:
            if self.players[seat] != None:
                filled_seats.append(seat)
        return filled_seats
    
    def get_filled_seats_with_players(self):
        filled_seats = []
        for seat in self.players:
            if self.players[seat] != None:
                filled_seats.append(self.players[seat])
        return filled_seats

    def get_remaining_players(self):
        remaining_players = []
        for seat in self.players:
            if self.players[seat] != None and self.players[seat].is_playing:
                remaining_players.append(self.players[seat])
        return remaining_players

    

    def button_change(self):

        filled_seats = self.get_filled_seats()
        filled_len = len(filled_seats)
        self.button = filled_seats[(filled_seats.index(self.button) + 1) % filled_len]
        print(f'new button assigned to: {self.button}')

        # assigning roles in player states        
        self.players[self.button].role = "button"
        self.players[filled_seats[(filled_seats.index(self.button) + 1) % filled_len]].role = "small_blind"
        self.players[filled_seats[(filled_seats.index(self.button) + 1) % filled_len]].remaining_chips -= int(self.small_blind_amount)
        self.players[filled_seats[(filled_seats.index(self.button) + 1) % filled_len]].chips_in_play += int(self.small_blind_amount)
        self.players[filled_seats[(filled_seats.index(self.button) + 1) % filled_len]].current_bet += int(self.small_blind_amount)
        self.players[filled_seats[(filled_seats.index(self.button) + 2) % filled_len]].role = "big_blind"
        self.players[filled_seats[(filled_seats.index(self.button) + 2) % filled_len]].remaining_chips -= int(self.big_blind_amount)
        self.players[filled_seats[(filled_seats.index(self.button) + 2) % filled_len]].chips_in_play += int(self.big_blind_amount)
        self.players[filled_seats[(filled_seats.index(self.button) + 2) % filled_len]].current_bet += int(self.big_blind_amount)
        self.players[filled_seats[(filled_seats.index(self.button) + 3) % filled_len]].role = "preflop_starter"

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
        self.winner = []
        self.deck = Deck().deck
        self.phase = "preflop"
        self.highest_bet = 0
        self.betting_over = False
        self.highest_bet = int(self.big_blind_amount)
        self.total_chips_in_play += int(self.small_blind_amount) + int(self.big_blind_amount)
        self.round_num += 1
        self.round_over = False

        # deal cards
        for seat in self.players:
            if self.players[seat] != None:
                self.players[seat].hand = [self.deck.pop(), self.deck.pop()]

        # assign roles
        self.button_change()
        filled_seats = self.get_filled_seats()
        for seat in filled_seats:
            if self.players[seat].role == "preflop_starter":
                self.betting_player_id = self.players[seat].id
                self.betting_player_seat = seat
                self.start_point = seat

    def deal_flop(self):
        # self.reset_bets()
        self.community_cards = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        self.phase = "flop"
        if not self.is_everyone_allin:
            self.betting_over = False

    def deal_turn(self):
        # self.reset_bets()
        self.community_cards.append(self.deck.pop())
        self.phase = "turn"
        if not self.is_everyone_allin:
            self.betting_over = False

    def deal_river(self):
        # self.reset_bets()
        self.community_cards.append(self.deck.pop())
        self.phase = "river"
        if not self.is_everyone_allin:
            self.betting_over = False

    def showdown(self):
        # self.reset_bets()
        print("showdown")
        self.phase = "showdown"
        self.get_winner()


    def get_winner(self):
        # get all players still in the game
        players_in_game = self.get_remaining_players()
        temp_community_cards = self.community_cards.copy()

        # user case where everyone has folded except one player
        index = 1
        tries = 0
        while(len(players_in_game) > 1):
            hand1_ = None
            hand1_ =players_in_game[0].hand.copy()
            hand1 = HandParser(hand1_)
            hand1 += temp_community_cards
            hand2_ = None
            hand2_ = players_in_game[index % len(players_in_game)].hand.copy()
            hand2 = HandParser(hand2_)
            hand2 += temp_community_cards

            hand1.parse()
            hand2.parse()

            if hand1 == hand2:
                index += 1
            elif hand1 > hand2: 
                seat = self.get_player_by_id(players_in_game[index % len(players_in_game)].id)
                self.players[seat].is_playing = False
                players_in_game.pop(index % len(players_in_game))
            else:
                seat = self.get_player_by_id(players_in_game[0].id)
                self.players[seat].is_playing = False
                players_in_game.pop(0)
                index = 1
            tries += 1
            if tries > 30:
                break
        
        # One winner
        if len(players_in_game) == 1:
            self.winner.append(players_in_game[0])
            seat = self.get_player_by_id(players_in_game[0].id)
            self.players[seat].remaining_chips += self.total_chips_in_play
            self.players[seat].is_playing = False
        # Multiple Winners
        else:
            print('winner not equal to 1')
            # split the pot
            self.winner = []
            for player in players_in_game:
                print("winner: " + player.name)
                self.winner.append(player)
                seat = self.get_player_by_id(player.id)
                self.players[seat].remaining_chips += self.total_chips_in_play / len(players_in_game)
                self.players[seat].is_playing = False
        self.round_over = True
        
    # def update_loser(self, seat):
    #     self.players[seat].is_playing = False
        # self.players[seat].remaining_chips -= self.players[seat].chips_in_play

    def fold(self, id):
        seat = self.get_player_by_id(id)
        self.players[seat].is_playing = False
        self.players[seat].bet_type = "fold"
        remaining_players = self.get_remaining_players()
        if len(remaining_players) == 1:
            self.showdown()
        else:
            self.betting_player_id = self.assign_next_better(id)
            self.betting_player_seat = self.get_player_by_id(self.betting_player_id)

    
    def bet(self, id, amount, type):
        seat = self.get_player_by_id(id)
        self.players[seat].remaining_chips -= amount
        self.players[seat].chips_in_play += amount
        self.players[seat].current_bet += amount
        self.total_chips_in_play += amount
        self.players[seat].bet_type = type
        filled_seats = self.get_filled_seats()
        if type == "allin":
            for seat in filled_seats:
                if self.players[seat].bet_type != "allin" and self.players[seat].is_playing:
                    self.is_everyone_allin = False
                    break
                self.is_everyone_allin = True
        if self.highest_bet < self.players[seat].current_bet:
            self.start_point = seat
        self.highest_bet = max(self.highest_bet, self.players[seat].current_bet)
        self.betting_player_id = self.assign_next_better(id)
        self.betting_player_seat = self.get_player_by_id(self.betting_player_id)


    def reset_bets(self):
        filled_seats = self.get_filled_seats()
        allin_players = []
        for seat in filled_seats:
            if self.players[seat].role == "small_blind":
                self.start_point = seat
        self.highest_bet = 0
        self.betting_over = True
        for seat in self.players:
            if self.players[seat] != None:
                self.players[seat].current_bet = 0
                self.players[seat].bet_type = None

    def assign_next_better(self, current_better_id):
        filled_seats = self.get_filled_seats() # gives a list of seats
        filled_len = len(filled_seats)
        current_better = self.get_player_by_id(current_better_id) # gives a seat
        current_better = filled_seats.index(current_better)
        next_better = (current_better + 1) % filled_len
        while self.players[filled_seats[next_better]].is_playing == False or self.players[filled_seats[next_better]].bet_type == "allin":
            next_better = (next_better + 1) % filled_len
        # if self.phase == "pre_flop" and self.players[filled_seats[next_better]].role == "preflop_starter" or self.phase != "pre_flop" and self.players[filled_seats[next_better]].role == "small_blind":
        if filled_seats[next_better] == self.start_point:
            if self.players[filled_seats[next_better]].current_bet == self.highest_bet:
                print("Betting Over")
                self.reset_bets()
                # self.betting_over = True
                return [p for p in self.get_filled_seats_with_players() if p.role == "small_blind"][0].id
        return self.players[filled_seats[next_better]].id





class Player:
    def __init__(self, id, name, join_code, avatar, is_host):
        self.id = id
        self.join_code = join_code
        self.name = name
        self.avatar = avatar
        self.is_host = is_host
        # self.original_chips = original_chips
        self.remaining_chips = 10000
        self.chips_in_play = 0
        self.current_bet = 0
        self.bet_type = None
        self.is_playing = True
        self.role = None
        self.hand = None

    def __getitem__(self):
        return self

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
        random.shuffle(deck)
        random.shuffle(deck)
        random.shuffle(deck)
        random.shuffle(deck)
        self.deck = deck

        # def get_deck_data():
        #     return deck

    

    
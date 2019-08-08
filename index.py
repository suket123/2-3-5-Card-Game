from flask import Flask, send_from_directory
import numpy as np
import json
from typing import Tuple, List

app = Flask(__name__)


class Card:

    SUITS = ['♠', '♥', '♣', '♦']
    SPECIALS = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

    def __init__(self, suit: int, card: int):
        self.suit = suit
        self.card = card
        self.string = self.__str__()

    def __repr__(self):
        card = str(self.card) if self.card not in Card.SPECIALS else Card.SPECIALS[self.card]
        return Card.SUITS[self.suit] + card

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other: 'Card'):
        return self.card == other.card and self.suit == other.suit

    def __lt__(self, other: 'Card'):
        return self.card < other.card


class IncompleteStateError(Exception): pass


class Game:

    MAJOR = Card(1, 7)
    MINOR = Card(0, 7)

    def __init__(self):
        self.state : List[Card] = []
        self.cards : Tuple[List[Card]] = self.distribute()
        self.scores : List[int] = [0, 0, 0]
        self.next_player: int = 0
        self.sir = -1

    def distribute(self):
        """
        Populates the cards list.
        """

        cards: List[Card] = []
        
        for i in range(4):
            for j in range(7, 15):
                if not (j == 7 and i in [2, 3]): 
                    cards.append(Card(i, j))

        np.random.shuffle(cards)
        return (cards[0:10], cards[10:20], cards[20:30])


    def find_sir(self, player_id) -> int:
        the_sir = int(input("Choose Sir: "))
        while ((the_sir < 0 or the_sir > 3)):
            the_sir = int(
                input("Incorrect input. Possible options from 0 to 3: Choose Sir: "))

        return the_sir


    def evaluate(self):
        if not len(self.state) == 3:
            raise IncompleteStateError('The card state is incomplete.')

        sirs = [card for card in self.state if card.suit == self.sir]
        if len(sirs) > 0: 
            winner =  self.state.index(max(sirs))
        else:
            valids = max([card for card in self.state if card.suit == self.state[0].suit])
            winner = self.state.index(valids)
        return (((self.next_player + 1) % 3) + winner) % 3


    def get_possible_plays(self) -> List['Card']:
        possible_plays = []
        if len(self.state) == 0 or len(self.state) == 3:
            for card in self.cards[self.next_player]:
                    possible_plays.append(card)
        else:
            suit_played = self.state[0].suit
            for card in self.cards[self.next_player]:
                if (card.suit == suit_played):
                    possible_plays.append(card)
            if (len(possible_plays) == 0):
                for card in self.cards[self.next_player]:
                    possible_plays.append(card)

        return possible_plays


    def play_hand(self, play):
        if len(self.state) == 3:
            self.state = []

        # Get the play
        plays = self.get_possible_plays()

        if play < 0 or play >= len(plays): return "Error"

        self.state.append(plays[play])

        self.cards[self.next_player].remove(plays[play])

        if len(self.state) == 3:
            self.next_player = game.evaluate()
            self.scores[self.next_player] += 1
        else:
            self.next_player = (self.next_player + 1) % 3

        return "Play made"


def encode(cards):
    return [card.__dict__ for card in cards]

game = Game()

@app.route("/play/<player>/<card>")
def play_card(player, card):
    try:
        player = int(player)
        card = int(card)
    except ValueError:
        return "Player and card must be an int"

    if player-1 == game.next_player:
        return str(game.play_hand(card))
    else:
        return "It is not your turn"


@app.route("/set_sir/<player>/<sir>")
def set_sir(player, sir):
    try:
        player = int(player)
        sir = int(sir)
    except ValueError:
        return "Player and sir must be an int"

    if player == 1 and len(game.cards[0]) == 10:
        game.sir = sir

    return "OK"


@app.route("/state")
def state():
    return json.dumps(game.state)


@app.route("/data/<player>")
def data(player):
    try:
        player = int(player)
    except ValueError:
        return "Player must be an int"

    return json.dumps({
        'turn': str(game.next_player+1),
        'playable': encode(game.get_possible_plays()) if game.next_player == player-1 else [],
        'all': encode(game.cards[player - 1]),
        'state': encode(game.state),
        'scores': game.scores,
        'sir': game.sir
    })
    return str(game.next_player+1)


@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

# while len(game.cards[0]) > 0:
#     game.play_hand()
# winner = np.argmax(np.array(game.scores) - [5, 3, 2])


import random

def rank_to_str(rank_id):
    if rank_id == 0:
        return "*Joker"
    elif rank_id == 1:
        return "Ace"
    elif rank_id == 11:
        return "Jack"
    elif rank_id == 12:
        return "Queen"
    elif rank_id == 13:
        return "King"
    elif 2 <= rank_id <= 10: # cards with 2 <= number <= 10
        return str(rank_id)
    else:
        return "RankError"
    
def suit_to_str(suit_id):
    if suit_id == 0:
        return "*Joker"
    elif suit_id == 1:
        return "Diamonds" # ""Ruiten"
    elif suit_id == 2:
        return "Hearts" # "harten"
    elif suit_id == 3: 
        return "Spades" # "Schoppen"
    elif suit_id == 4:
        return "Clubs" # "Klaveren"
    else:
        return "SuitError"

class PlayingCard():
    def __init__ (self, rank_id, suit_id):
        self.suit_id = suit_id
        self.rank_id = rank_id

    def short_name(self):
        if 2 <= self.rank_id <= 10:
            return rank_to_str(self.rank_id) + suit_to_str(self.suit_id)[0]
        else:
            return rank_to_str(self.rank_id)[0] + suit_to_str(self.suit_id)[0]
        
    def long_name(self):
        if self.suit_id == 0:
            return rank_to_str(self.rank_id)[1:]
        else:
            return rank_to_str(self.rank_id) + " of " + suit_to_str(self.suit_id)

    def __str__(self):
        return self.long_name()
    
    def __repr__(self):
        return self.short_name()


def standard_deck(jokers):
    deck = []
    # We add each card to the playing stack once 4 * 13 = 52 cards
    for suit_id in range(1, 4+1):
        for rank_id in range(1, 13+1):
            deck.append(PlayingCard(rank_id, suit_id))

    # add two jokers to the deck
    for i in range (0, jokers):
        deck.append(PlayingCard(0, 0)) 
    
    random.shuffle(deck) # shuffles the deck
    return deck


class GameState():
    def __init__(self, turn = 0, hands = [[]], draw_stack = [], discard_stack = []):
        self.hands = hands # assumes the robots hand is 0 and always exists, the player hand(s) are >= 1
        self.draw_stack = draw_stack # first element is the top card (first card to be drawn)
        self.discard_stack = discard_stack # first element is the top card (visible to all players)
        assert turn < len(self.hands), "Turn must be a valid player id"
        self.turn = turn # stores the current player's turn

    def __str__(self):
        return "turn: " + str(self.turn) + ", hands: " + str(self.hands) + ", discard_stack: " + str(self.discard_stack) + ", draw_stack: " + str(self.draw_stack)
    
    def num_players(self):
        return len(self.hands)

    def top_card(self):
        assert 1 <= len(self.discard_stack), "Discard stack is empty"

        return self.discard_stack[0]
    
    def draw_card(self, player_id):
        assert 1 <= len(self.draw_stack), "Draw stack is empty"
        assert player_id < len(self.hands), "Player id out of range"

        self.hands[player_id].append(self.draw_stack.pop(0))
        return self.hands[player_id][-1]

    def draw_cards(self, player_id, amount):
        assert amount <= len(self.draw_stack), "Draw stack is not large enough"
        assert player_id < len(self.hands), "Player id out of range"
        assert amount > 0, "Amount must be positive"

        for i in range(amount):
            self.hands[player_id].append(self.draw_stack.pop(0))
        return self.hands[player_id][-amount:]

    def play_card(self, player_id, card_index):
        assert player_id < len(self.hands), "Player id out of range"
        assert 0 <= card_index < len(self.hands[player_id]), "Card index out of range"

        self.discard_stack.insert(0, self.hands[player_id].pop(card_index))

    def set_turn(self, player_id):
        assert player_id < len(self.hands), "Player id out of range"

        self.turn = player_id


class Pesten_GameState(GameState):
    def __init__(self, hands = [[]], turn = 0, draw_stack = standard_deck(jokers=2), discard_stack = [PlayingCard(0,0)], active_suit = 0, pestkaarten_sum = 0, skip_next_turn = False):
        super().__init__(turn, hands, draw_stack, discard_stack)
        assert 0 <= active_suit <= 4, "Active suit must be a valid suit id"
        assert 0 <= pestkaarten_sum, "Pestkaarten sum must be positive"
        assert 1 <= len(discard_stack), "discard_stack must have at least one card"
        assert not (0 < pestkaarten_sum) or (discard_stack[0].rank_id in [0,2]), "pestkaarten_sum above 0 must imply that the top card is a pestkaart"
        
        self.active_suit = active_suit # only used when the last player card is a Jack (can switch to any suit)
        self.pestkaarten_sum = pestkaarten_sum # sum of the total cards the next player must draw (if they can't play a pestkaart themselves)
        self.skip_next_turn = skip_next_turn # stores if the next player must skip their turn

        
    def setup(self, player_count): # sets up the game if it isn't already (resets the game ready to play)
        assert player_count > 1, "Player count must be at least 2"

        self.draw_stack = standard_deck(jokers=2)
        self.discard_stack = []

        self.hands = [[] for i in range(player_count)]
        for i in range(player_count): # all players draw 7 cards
            self.draw_cards(i, 7)

        self.discard_stack.insert(0, self.draw_stack.pop(0)) # draw the top card and put it on the discard stack
        while (self.top_card().rank_id in [0, 2]): # if the top card is a 'pestkaart' (joker or rank 2 card)
            self.discard_stack.insert(0, self.draw_stack.pop(0)) # draw the top card and put it on the discard stack

        self.active_suit = self.top_card().suit_id # set the active suit to the suit of the top card
        self.pestkaarten_sum = 0
        self.skip_next_turn = False
        # TODO: uncomment the next line to randomise the starting player
        self.turn = 0 # random.randint(0, player_count-1) # a random player starts the game

    def __str__(self):
        return super().__str__() + ", active_suit: " + str(self.active_suit) + ", pestkaarten_sum: " + str(self.pestkaarten_sum) + ", skip_next_turn: " + str(self.skip_next_turn)

def main():
    game = Pesten_GameState()
    game.setup(2)
    print(game)

    game.play_card(0, 1)
    print(game)


if __name__ == "__main__":
    main()



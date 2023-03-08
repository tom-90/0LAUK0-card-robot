import random
import numpy as np
import copy

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
        return "Diamonds" # "Ruiten"
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

# Returns a multiset containing 52 cards (4 suits * 13 ranks) and the specified number of jokers
def standard_deck(jokers):
    deck = []
    # We add each card to the playing stack once 4 * 13 = 52 cards
    for suit_id in range(1, 4+1):
        for rank_id in range(1, 13+1):
            deck.append(PlayingCard(rank_id, suit_id))

    # Add jokers to the deck
    for i in range (0, jokers):
        deck.append(PlayingCard(0, 0)) 
    
    return deck


class GameState():
    def __init__(self, turn = 0, hands = [[]], draw_stack = [], discard_stack = []):
        self.hands = hands # Assumes the robots hand is the list at index 0 and assumes this list always exists, the player hand(s) are lists with index >= 1
        self.draw_stack = draw_stack # Unordered list of cards (a card can appear multiple times, like the 2 jokers)
        self.discard_stack = discard_stack # First element is the top card (visible to all players at current time instance)
        assert turn < len(self.hands), "Turn must be a valid player id"
        self.turn = turn # Stores the current player's turn

    def __str__(self):
        return "turn: " + str(self.turn) + ", hands: " + str(self.hands) + ", discard_stack: " + str(self.discard_stack) + ", draw_stack: " + str(self.draw_stack)
    
    def num_players(self):
        return len(self.hands)

    def top_card(self):
        assert 1 <= len(self.discard_stack), "Discard stack is empty"

        # The first element of the discard_stack list is the top card
        return self.discard_stack[0]

    def draw_cards(self, player_id, amount = 1):
        assert amount <= len(self.draw_stack), "Draw stack is not large enough"
        assert player_id < len(self.hands), "Player id out of range"
        assert amount > 0, "Amount must be positive"

        for i in range(0, amount):
            self.hands[player_id].append(self.draw_stack.pop(random.randrange(len(self.draw_stack))))
        # Return the cards that have been drawn
        return self.hands[player_id][-amount:]

    def play_card(self, player_id, card_index):
        assert player_id < len(self.hands), "Player id out of range"
        assert 0 <= card_index < len(self.hands[player_id]), "Card index out of range"

        self.discard_stack.insert(0, self.hands[player_id].pop(card_index))

    def advance_turn(self):
        self.turn = (self.turn + 1) % self.num_players()

    def has_won(self, player_id):
        return False



class Pesten_GameState(GameState):
    def __init__(self, hands = [[]], turn = 0, draw_stack = standard_deck(jokers=2), discard_stack = [PlayingCard(0,0)], pestkaarten_sum = 0, skip_next_turn = False):
        super().__init__(turn, hands, draw_stack, discard_stack)
        assert 0 <= pestkaarten_sum, "Pestkaarten sum must be positive"
        assert 1 <= len(discard_stack), "discard_stack must have at least one card"
        assert not (0 < pestkaarten_sum) or (discard_stack[0].rank_id in [0,2]), "pestkaarten_sum above 0 must imply that the top card is a pestkaart"
        
        self.pestkaarten_sum = pestkaarten_sum # Stores the sum of the total cards the next player must draw (if they can't play a pestkaart themselves)
        self.skip_next_turn = skip_next_turn # Stores whether the next player must skip their turn or not
        
    # Sets up the gamestate if it isn't set up already (resets the gamestate ready to play)
    def setup(self, player_count): 
        assert player_count > 1, "Player count must be at least 2" # You cannot play a game of "Pesten" with less than two players

        self.draw_stack = standard_deck(jokers=2)
        self.discard_stack = []

        # Create empty list for each player, representing an empty hand for each player
        self.hands = [[] for i in range(player_count)]
        # All players draw 7 cards / are given 7 cards
        for i in range(player_count): 
            self.draw_cards(i, 7)

        self.discard_stack.insert(0, self.draw_stack.pop(random.randrange(len(self.draw_stack)))) # Draw a random card and put it on the discard stack
        while (self.top_card().rank_id in [0, 2]): # If the top card is a 'pestkaart' (joker or rank 2 card)
            self.discard_stack.insert(0, self.draw_stack.pop(random.randrange(len(self.draw_stack)))) # Draw a random card and put it on the discard stack

        self.pestkaarten_sum = 0
        self.skip_next_turn = False
        # TODO: uncomment the next line to randomise the starting player
        self.turn = 0 # random.randint(0, player_count-1) # a random player starts the gamestate

    # The given player plays the specified card, if card_index == -1, the player draws a card instead
    # Returns True if the turn ends, False if the player can still play
    def play_card(self, player_id, card_index, muted = False):
        if (card_index == -1): # If the player chooses to draw a card
            if (0 < self.pestkaarten_sum): # If the player must draw cards
                self.draw_cards(player_id, self.pestkaarten_sum) # The player draws the mandatory number of cards 
                if not muted:
                    print(f"Player {self.turn} draws {self.pestkaarten_sum} cards.")
                self.pestkaarten_sum = 0
                return False # The player must still play after drawing the forced cards
            else:
                self.draw_cards(player_id, amount=1)
                if not muted:
                    print(f"Player {self.turn} draws 1 card.")
                return True # Drawing a card by choice, ends the turn
        else:
            chosen_move = self.hands[self.turn][card_index]
            super().play_card(player_id, card_index) # Moves the card from the hand to the top of the discard_stack
            if not muted:
                print(f"Player {self.turn} plays {chosen_move}")
            turn_over = True 
            if (chosen_move.rank_id in [0,2]): # If chosen move is playing a "pestkaart"
                self.pestkaarten_sum += (5 if chosen_move.rank_id == 0 else 2) # Increase pestkaarten_sum accordingly
                if not muted:
                    print(f"the next player needs to draw {self.pestkaarten_sum} new cards.")
            elif (chosen_move.rank_id == 7): # If chosen move is playing a card with rank 7, the turn is not over
                if not muted:
                    print(f"Player {self.turn} takes another turn.")
                turn_over = False
            elif (chosen_move.rank_id == 8): # If chosen move is playing a card with rank 8, the turn of the next player is skipped
                if not muted:
                    print(f"The next player is forced to skip their turn.")
                self.skip_next_turn = True

        return turn_over

    def draw_cards(self, player_id, amount = 1):
        assert player_id < len(self.hands), "Player id out of range"
        assert amount > 0, "Amount must be positive"

        if (len(self.draw_stack) < amount):
            print("Adding all but the top card of the discard stack to the draw stack")
            self.draw_stack += self.discard_stack[1:]
            self.discard_stack = [self.discard_stack[0]]

        return super().draw_cards(player_id, amount) # Draw a card from the updated draw_stack
    
    def has_won(self, player_id):
        return len(self.hands[player_id]) == 0

    # Gives a list of valid moves for the given player, this always includes the option to draw a card (-1)
    def valid_moves(self, player_id):
        valid_moves = []
        if (0 < self.pestkaarten_sum):
            for i in range(len(self.hands[player_id])):
                if (self.hands[player_id][i].rank_id in [0,2]):
                    valid_moves.append(i)
        else:
            for i in range(len(self.hands[player_id])):
                if (self.hands[player_id][i].suit_id == self.top_card().suit_id or self.hands[player_id][i].rank_id == self.top_card().rank_id or self.hands[player_id][i].rank_id == 0 or self.top_card().rank_id == 0):
                    valid_moves.append(i)

        valid_moves.append(-1) # -1 stands for voluntarily drawing a card
        return valid_moves
    
    # Gives the probability that the opponent will be able to place a card on the discard stack with the knowledge about the discard_stack and your own hand
    # This function will be used by the robot to decide which move is a suiting move to make
    def chance_valid_card(self):
        num_valid_cards_opponent = self.valid_moves(1)
        total_nr_cards = len(standard_deck) + 2 # 2 jokers

        num_cards_discard_stack = len(self.discard_stack)
        num_cards_robot_hand = len(self.hands[0])
        num_cards_opponent_has_not = num_cards_discard_stack + num_cards_robot_hand

        return pow(((num_valid_cards_opponent - num_cards_opponent_has_not) / (total_nr_cards - num_cards_opponent_has_not)), len(self.hands[1]))
    
    # Gives a score to the resulting state after the current player plays the given card
    # Used by the robot to decide which move is a suiting move to make 
    def move_score(self, player_id, card_index):
        copy_state = copy.deepcopy(self)
        old_hand_size = len(copy_state.hands[player_id])
        if (copy_state.play_card(copy_state.turn, card_index, muted=True)):
            copy_state.advance_turn()
            
        # TODO: experiment with this formula and weights
        return -20 * len(copy_state.hands[player_id]) + (- 5 * copy_state.chance_valid_card()) + (old_hand_size - len(copy_state.hands[player_id])) - (0 if len(copy_state.valid_moves(player_id)) > 1 else 10) + (10 if copy_state.turn == player_id else 0) + copy_state.pestkaarten_sum * (10 if copy_state.turn != player_id else -10)

    def __str__(self):
        return super().__str__() + ", pestkaarten_sum: " + str(self.pestkaarten_sum) + ", skip_next_turn: " + str(self.skip_next_turn)

def main():
    gamestate = Pesten_GameState()
    gamestate.setup(2)
    print(gamestate)

    # Print function to test move_score function
    for move in gamestate.valid_moves(0):
        print(move, gamestate.move_score(0, move))

    gamestate.play_card(0, -1)
    print(gamestate)

if __name__ == "__main__":
    main()



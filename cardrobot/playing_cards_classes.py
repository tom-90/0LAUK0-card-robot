import random
import copy
from collections import Counter

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
        return f"turn: {self.turn}, hands: {self.hands}, discard_stack: {self.discard_stack}, draw_stack: {self.draw_stack}"
    
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

    def next_player(self):
        return (self.turn + 1) % self.num_players()

    def advance_turn(self):
        self.turn = self.next_player()

    # ALERT: THIS FUNCTION MUST BE OVERRIDEN IN THE SUBCLASS
    def has_won(self, player_id):
        return False



class Pesten_GameState(GameState):
    def __init__(self, hands = [[]], turn = 0, draw_stack = standard_deck(jokers=2), discard_stack = [PlayingCard(0,0)], pestkaarten_sum = 0, skip_next_turn = False, play_direction = 1):
        super().__init__(turn, hands, draw_stack, discard_stack)
        assert 0 <= pestkaarten_sum, "Pestkaarten sum must be positive"
        assert 1 <= len(discard_stack), "discard_stack must have at least one card"
        assert not (0 < pestkaarten_sum) or (discard_stack[0].rank_id in [0,2]), "pestkaarten_sum above 0 must imply that the top card is a pestkaart"
        
        self.pestkaarten_sum = pestkaarten_sum # Stores the sum of the total cards the next player must draw (if they can't play a pestkaart themselves)
        self.skip_next_turn = skip_next_turn # Stores whether the next player must skip their turn or not
        self.play_direction = play_direction # Stores the direction of play (1 = clockwise, -1 = counterclockwise)
        
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
        self.play_direction = 1
        # TODO: uncomment the next line to randomise the starting player
        self.turn = 0 # random.randint(0, player_count-1) # a random player starts the gamestate
    
    def __str__(self):
        return f"{super().__str__()}, pestkaarten_sum: {self.pestkaarten_sum}, skip_next_turn: {self.skip_next_turn}, play_direction: {self.play_direction}"


    # overrides the next_player function in the superclass (allows for the play direction to be changed)
    def next_player(self):
        return (self.turn + self.play_direction) % self.num_players()

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
            elif (chosen_move.rank_id == 1): # If chosen move is an ace, the direction of play is reversed
                self.play_direction *= -1
                if not muted:
                    print(f"The direction of play has been reversed to {'clockwise' if self.play_direction == 1 else 'anti-clockwise'}.")
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
    
    # returns whether the given card can be played in the current gamestate
    def is_valid_card(self, playingcard):
        if (0 < self.pestkaarten_sum):
            return playingcard.rank_id in [0,2]
        else:
            return ((playingcard.suit_id in [0, self.top_card().suit_id]) or (self.top_card().rank_id in [0, playingcard.rank_id]))

    # Gives a list of valid moves for the given player, this always includes the option to draw a card (-1)
    def valid_moves(self, player_id):
        valid_moves = [index for index, card in enumerate(self.hands[player_id]) if self.is_valid_card(card)]
        valid_moves.append(-1) # -1 stands for voluntarily drawing a card
        return valid_moves
    
    # Gives the probability that the specified player will be able to place a card on the discard stack with the knowledge about the discard_stack and the robots hand
    # This function will be used by the robot in move_score() to decide which move is a suitable move to make
    def chance_player_has_valid_card(self, robot_players, player_id):
        if (player_id not in robot_players):
            known_cards = self.discard_stack
            for robot_id in robot_players:
                known_cards += self.hands[robot_id]
            unknown_cards = list(Counter(standard_deck(2)) - Counter(known_cards)) # preserves potential duplicate jokers in the deck
            valid_unknown_cards = [x for x in unknown_cards if self.is_valid_card(x)]
            
            chance_1_valid = float(len(valid_unknown_cards)) / len(unknown_cards) # chance 1 unknown card is valid
            chance_1_invalid = 1.0 - chance_1_valid # chance 1 unknown card is invalid
            chance_all_cards_invalid = chance_1_invalid ** len(self.hands[player_id]) # chance that all cards in the players hand are invalid
        
            return 1.0 - chance_all_cards_invalid # chance that at least 1 valid card is in the players hand
        else:
            return 1.0 if len(self.valid_moves(player_id)) > 1 else 0.0
    

    # Gives a score to the resulting state after the current player_id (only used by the robot) makes the move
    # Used by the robot to decide which move is a suiting move to make 
    def move_score(self, player_id, card_index):
        copy_state = copy.deepcopy(self)
        old_hand_size = len(copy_state.hands[player_id])
        old_pestkaarten_sum = copy_state.pestkaarten_sum # The pestkaarten_sum value before the move is made
        old_top_card = copy_state.top_card() # The top card of the discard stack before the move is made

        # the 2 lines below make the move and if applicable advances the turn (so the score is calculated 1 turn in the future)
        if (copy_state.play_card(copy_state.turn, card_index, muted=True)):
            copy_state.advance_turn()
            
        # TODO: experiment with this formula and weights

                # The number of cards in the hand of the player in the resulting gamestate
        score = (200 - 20 * len(copy_state.hands[player_id]) \
                # The chance that the other player will be able to play a card in the resulting gamestate
                - 20 * copy_state.chance_player_has_valid_card([0], copy_state.turn) \
                # The difference between the number of cards in hand after making the move
                + (old_hand_size - len(copy_state.hands[player_id])) \
                # Penalize for having no valid moves in the resulting gamestate
                - 10 * (0 if len(copy_state.valid_moves(player_id)) > 1 else 1) \
                # Reward for again getting the next turn  in the resulting gamestate
                + 50 * (1 if copy_state.turn == player_id else 0) \
                # If pestkaarten_sum is greater than zero before player has made its move, reward for playing a pestkaart.
                + 10 * (1 if old_pestkaarten_sum > 0 and copy_state.pestkaarten_sum > old_pestkaarten_sum else 0) \
                # Penalize for playing a pestkaart when pestkaarten_sum is not greater than zero before player has made its move 
                # and when next_player has relatively many cards left.
                - 10 * (1 if old_pestkaarten_sum <= 0 and len(copy_state.hands[copy_state.turn]) > 4 else 0) \
                # small reward for playing a non-standard card
                + 5 * (1 if old_top_card != copy_state.top_card() and copy_state.top_card().rank_id in [0,1,2,7,8] else 0) \
                )
        return score


def main():
    gamestate = Pesten_GameState()
    gamestate.setup(2)
    print(gamestate)

    # Print function to test move_score function
    for move in gamestate.valid_moves(0):
        print(move, gamestate.move_score(0, move))

    # gamestate.play_card(0, -1)
    # print(gamestate)

if __name__ == "__main__":
    main()



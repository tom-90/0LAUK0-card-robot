from pesten.player import PestenPlayer
from game.cards import Card
from copy import deepcopy
from mcts import mcts
import random
from pesten.types import PestenOutputType, PestenInputType
import numpy as np
from pesten.interface import StateInterface

# Converts arbitrary scores to probabilities using a modified softmax function
# If difficulty = 0, the function returns a uniform probability for all scores 
# If 0 < difficulty < 1, the function gives a higher probability to the highest score 
# If difficulty = 1, the function gives approximately a probability of ~1 to the highest score, and ~0 to all other scores
def softmax_with_difficulty(scores, diff):
    b_x = np.power(1.0 + (diff ** 1.25), scores - np.max(scores)) # Note to self: the power of the difficulty (>= 1) can be played with to change relative probabilities
    return b_x / b_x.sum()

class PestenRobotPlayer(PestenPlayer):
    type = "robot"

    # Gives a list of valid moves for the given player, this always includes the option to draw a card (-1)
    def get_valid_moves(self):
        valid_moves = [card for card in self.hand if self.state.is_valid_card(card)]
        valid_moves.append(-1) # -1 stands for voluntarily drawing a card
        return valid_moves

    # Gives a score to the resulting state after the current player_id (only used by the robot) makes the move
    # Used by the robot to decide which move is a suiting move to make 
    def get_move_score(self, card: Card):
        copied_state = deepcopy(self.state)
        copied_player: PestenRobotPlayer = copied_state.get_current_player()
        old_hand_size = len(copied_player.hand)
        old_pestkaarten_sum = copied_state.pestkaarten_sum
        old_top_card = copied_state.get_top_card()

        # the 2 lines below make the move and if applicable advances the turn (so the score is calculated 1 turn in the future)
        if (copied_player.do_move(card, virtual=True)):
            copied_state.advance_turn()

        next_player = copied_state.get_current_player()
            
        # TODO: experiment with this formula and weights

                # The number of cards in the hand of the player in the resulting gamestate
        score = (200 - 20 * len(copied_player.hand) \
                # The chance that the other player will be able to play a card in the resulting gamestate
                - 20 * copied_player.get_chance_player_has_valid_card() \
                # The difference between the number of cards in hand after making the move
                + (old_hand_size - len(copied_player.hand)) \
                # Penalize for having no valid moves in the resulting gamestate
                - 10 * (0 if len(copied_player.get_valid_moves()) > 1 else 1) \
                # Reward for again getting the next turn in the resulting gamestate
                + 5 * (1 if next_player == copied_player else 0) \
                # If pestkaarten_sum is greater than zero before player has made its move, reward for playing a pestkaart.
                + 5 * (1 if old_pestkaarten_sum > 0 and copied_state.pestkaarten_sum > old_pestkaarten_sum else 0) \
                # Penalize for playing a pestkaart when pestkaarten_sum is not greater than zero before player has made its move 
                # and when next_player has relatively many cards left.
                - 10 * (1 if old_pestkaarten_sum <= 0 and next_player != copied_player and len(next_player.hand) > 4 else 0) \
                # small reward for playing a card with a special effect
                + 3 * (1 if old_top_card != copied_state.get_top_card() and copied_state.get_top_card().rank_id in [0,1,2,7,8] else 0) \
                )
        return score

    # Gives the probability that the specified player will be able to place a card on the discard stack with the knowledge about the discard_stack and the robots hand
    # This function will be used by the robot in move_score() to decide which move is a suitable move to make
    def get_chance_player_has_valid_card(self):
        return 1.0 if len(self.get_valid_moves()) > 1 else 0.0

    # The given player plays the card indexed by `move`, if move == -1, the player draws cards instead
    # Returns True if the turn ends, False if the player can still play
    def do_move(self, move: Card | int, virtual = False):
        if (move == -1): # If the player chooses to draw a card
            if (0 < self.state.pestkaarten_sum): # If the player must draw cards
                self.draw_cards(self.state.pestkaarten_sum, virtual) # The player draws the mandatory number of cards 
                self.state.pestkaarten_sum = 0
                return False # The player must still play after drawing the forced cards
            else:
                self.draw_cards(1, virtual)
                return True # Drawing a card by choice, ends the turn
        else:
            if not virtual:
                self.state.input(PestenInputType.WAIT_FOR_TOP_CARD, move) # wait until the card is on the discard stack
                self.state.output(PestenOutputType.PLAYER_PLAYS, self, move)

            self.hand -= move
            self.state.discard_stack += move

            return self.state.apply_card_effect(move, virtual)
        
    def draw_cards(self, amount: int = 1, virtual = False):
        assert 1 <= amount, "amount must be at least 1"

        if not virtual:
            self.state.output(PestenOutputType.PLAYER_DRAWS, self, amount)

        if len(self.state.draw_stack) < amount:
            self.state.reshuffle(virtual)

        for _ in range(amount):
            card = self.state.draw_stack.pop() # Will return UnknownCard

            if not virtual:
                card = self.state.input(PestenInputType.READ_DRAWN_CARD)

            self.hand += card

    def do_turn(self, difficulty: float = 0.0, use_mcts=False):
        self.state.output(PestenOutputType.PLAYER_TURN, self)
        self.use_mcts = use_mcts
        turn_over = False
        while not turn_over and not self.state.is_finished(True):
            if self.use_mcts:
                initialState = StateInterface(self.state, self.hand, self.state.pestkaarten_sum)
                searcher = mcts(timeLimit=1000)             # iterationLimit=500
                action = searcher.search(initialState=initialState)
                if action != -1:
                    move = Card(action.rank_id, action.suit_id)
                else:
                    move = -1
                print("Action is " + str(move))
                print("Robot hand:" + str(self.hand))
                print("Discard stack:" + str(self.state.discard_stack))
                turn_over = self.do_move(move)
            else:
                # Obtains the list of valid moves
                valid_moves_lst = self.get_valid_moves()

                # Obtains a list of scores for each valid move
                valid_moves_scores = [self.get_move_score(move) for move in valid_moves_lst]
                valid_moves_probs = softmax_with_difficulty(valid_moves_scores, difficulty)

                self.state.output(PestenOutputType.ROBOT_MOVE_STATS, self, valid_moves_lst, valid_moves_scores, valid_moves_probs)

                # Randomly chooses a move weighted on the probabilities, chosen_move == -1 means drawing a card
                chosen_move = random.choices(valid_moves_lst, weights=valid_moves_probs)[0] 

                # The chosen move is made and turn_over is updated accordingly
                turn_over = self.do_move(chosen_move)

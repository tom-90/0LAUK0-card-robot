from playing_cards_classes import PlayingCard, standard_deck
import random
import copy
from collections import Counter
import numpy as np



# TODO: returns the top card of the discard stack as seen by the camera
def camera_top_card():
    return PlayingCard(3,1)

# TODO: returns the card that is temporarily visible to the robot (to be placed in their hand)
def camera_robot_card():
    return PlayingCard(4,1)

# TODO: the program waits until the specified card is seen on the discard stack (the robot plays this card)
def camera_wait_until_top_card(card):
    print(f"Robot is playing: {card}")
    return

    # while (camera_top_card() != card):
    #     pass


# TODO: returns the new card the human player plays on the discard stack 
# or an integer equal to the number of drawn cards
# note that it is possible that a joker is played on top of a joker (the top card remains the same)
def camera_detect_played_card():
    return PlayingCard(5,1)



# Converts arbitrary scores to probabilities using a modified softmax function
# If difficulty = 0, the function returns a uniform probability for all scores 
# If 0 < difficulty < 1, the function gives a higher probability to the highest score 
# If difficulty = 1, the function gives approximately a probability of ~1 to the highest score, and ~0 to all other scores
def softmax_with_difficulty(scores, diff):
    b_x = np.power(1.0 + (diff ** 3), scores - np.max(scores)) # Note to self: the power of the difficulty (>= 1) can be played with to change relative probabilities
    return b_x / b_x.sum()


class Pesten_Unknown_GameState():
    def __init__(self, turn = 0, hands = [[], 0], draw_stack_count = (4*13)+2, discard_stack = [PlayingCard(0,0)], pestkaarten_sum = 0, skip_next_turn = False, play_direction = 1):
        assert 2 <= len(hands), "Player count must be at least 2" # You cannot play a game of "Pesten" with less than two players
        self.hands = hands # Stores the hands of each player, for the robots this is a list of PlayingCards, for the player this is an integer equal to the number of cards in their hand
        assert 0 <= turn < len(hands), "turn must be less than the number of players"
        self.turn = turn # Stores the index of the player whose turn it is
        assert 0 <= draw_stack_count, "draw_stack_count must be positive"
        self.draw_stack_count = draw_stack_count # Stores the number of cards left in the draw stack
        assert 1 <= len(discard_stack), "discard_stack must have at least one card"
        assert not (0 < pestkaarten_sum) or (discard_stack[0].rank_id in [0,2]), "pestkaarten_sum above 0 must imply that the top card is a pestkaart"
        self.discard_stack = discard_stack # Stores the discard stack, a list of PlayingCards with at least 1 element
        assert 0 <= pestkaarten_sum, "Pestkaarten sum must be positive"
        self.pestkaarten_sum = pestkaarten_sum # Stores the sum of the total cards the next player must draw (if they can't play a pestkaart themselves)
        self.skip_next_turn = skip_next_turn # Stores whether the next player must skip their turn or not
        assert play_direction in [1, -1], "play_direction must be either 1 or -1"
        self.play_direction = play_direction # Stores the direction of play (1 = clockwise, -1 = counterclockwise)
        
    def __str__(self):
        return f"turn: {self.turn}, hands: {self.hands}, draw_stack: {self.draw_stack_count}, discard_stack: {self.discard_stack}, pestkaarten_sum: {self.pestkaarten_sum}, skip_next_turn: {self.skip_next_turn}, play_direction: {self.play_direction}"
        
    # Sets up the gamestate if it isn't set up already (resets the gamestate ready to play)
    def setup(self, is_robot_list = [True, False]): 
        assert 2 <= len(is_robot_list), "Player count must be at least 2" # You cannot play a game of "Pesten" with less than two players
        
        # TODO: uncomment the next line to randomise the starting player
        self.turn = 0 # random.randint(0, len(is_robot_list)-1) # a random player starts the gamestate

        self.draw_stack = (4*13)+2
        
        self.hands = []
        # All players draw 7 cards from the draw stack
        for i in range(len(is_robot_list)):
            if is_robot_list[i]:
                self.hands.append([])
                self.draw_cards(i, 7) # should see these in the camera and subtract from draw_stack_count
            else:
                self.hands.append(0)
                self.draw_cards(i, 7) # subtracts from draw_stack_count

        self.pestkaarten_sum = 0
        self.skip_next_turn = False
        self.play_direction = 1

        self.discard_stack = []

        self.discard_stack.insert(0, camera_top_card()) # TODO: draw one card and add it to the discard stack
        self.draw_stack_count -= 1
        while (self.top_card().rank_id in [0, 2]):
            # TODO: wait until the top card is not a pestkaart (joker or rank 2 card)
            self.discard_stack.insert(0, camera_top_card())
            self.draw_stack_count -= 1

    def draw_cards(self, player_index, amount = 1):
        assert 0 <= player_index < len(self.hands), "player_index must be between 0 and the number of players"
        assert 1 <= amount, "amount must be at least 1"

        if self.draw_stack_count < amount:
            # TODO: wait until all cards from the discard stack except the top card are shuffled and added to the draw stack
            self.draw_stack_count += len(self.discard_stack) - 1
            self.discard_stack = [self.discard_stack[0]]

        if self.is_robot(player_index):
            for i in range(amount):
                self.hands[player_index].append(camera_robot_card()) # wait until the robot has seen all drawn cards
        else:
            self.hands[player_index] += amount

        self.draw_stack_count -= amount

    def is_robot(self, player_id):
        return isinstance(self.hands[player_id], list)
    
    def has_won(self, player_id):
        if self.is_robot(player_id):
            return len(self.hands[player_id]) == 0
        else:
            return self.hands[player_id] == 0
    
    def num_players(self):
        return len(self.hands)

    def top_card(self):
        assert 1 <= len(self.discard_stack), "Discard stack is empty"
        return self.discard_stack[0] # The first element of the discard_stack list is the top card
    
    def number_of_cards(self, player_id):
        if self.is_robot(player_id):
            return len(self.hands[player_id])
        else:
            return self.hands[player_id]

    def next_player(self):
        return (self.turn + self.play_direction) % self.num_players()

    def advance_turn(self):
        self.turn = self.next_player()

    # returns whether the given card can be played in the current gamestate
    def is_valid_card(self, playingcard):
        if (0 < self.pestkaarten_sum):
            return playingcard.rank_id in [0,2]
        else:
            return ((playingcard.suit_id in [0, self.top_card().suit_id]) or (self.top_card().rank_id in [0, playingcard.rank_id]))
        
    # Gives a list of valid moves for the given player, this always includes the option to draw a card (-1)
    def valid_moves(self, player_id):
        assert self.is_robot(player_id), "Player must be a robot to call this function"
        valid_moves = [index for index, card in enumerate(self.hands[player_id]) if self.is_valid_card(card)]
        valid_moves.append(-1) # -1 stands for voluntarily drawing a card
        return valid_moves
    
    # applies the special effect of the given card if it has any
    # returns whether the turn is over or not
    def card_effect(self, card, muted = False):
        if (card.rank_id in [0,2]): # If chosen move is playing a "pestkaart"
            self.pestkaarten_sum += (5 if card.rank_id == 0 else 2) # Increase pestkaarten_sum accordingly
            if not muted:
                print(f"the next player needs to draw {self.pestkaarten_sum} new cards.")
        elif (card.rank_id == 1): # If chosen move is an ace, the direction of play is reversed
            self.play_direction *= -1
            if not muted:
                print(f"The direction of play has been reversed to {'clockwise' if self.play_direction == 1 else 'anti-clockwise'}.")
        elif (card.rank_id == 7): # If chosen move is playing a card with rank 7, the turn is not over
            if not muted:
                print(f"The player takes another turn.")
            return False
        elif (card.rank_id == 8): # If chosen move is playing a card with rank 8, the turn of the next player is skipped
            if not muted:
                print(f"The next player is forced to skip their turn.")
            self.skip_next_turn = True
        return True

    # The given player plays the card indexed by `move`, if move == -1, the player draws cards instead
    # Returns True if the turn ends, False if the player can still play
    def do_move(self, player_id, move, muted = False):
        if (move == -1): # If the player chooses to draw a card
            if (0 < self.pestkaarten_sum): # If the player must draw cards
                if not muted:
                    print(f"Player {player_id} draws {self.pestkaarten_sum} cards.")
                self.draw_cards(player_id, self.pestkaarten_sum) # The player draws the mandatory number of cards 
                self.pestkaarten_sum = 0
                return False # The player must still play after drawing the forced cards
            else:
                if not muted:
                    print(f"Player {player_id} draws 1 card.")
                self.draw_cards(player_id, amount=1)
                return True # Drawing a card by choice, ends the turn
        else:
            chosen_card = self.hands[player_id][move]
            camera_wait_until_top_card(chosen_card) # wait until the card is on the discard stack
            self.discard_stack.insert(0, self.hands[player_id].pop(move)) # Remove the card from the hand and add it to the top of the discard stack
            if not muted:
                print(f"Player {player_id} plays: {chosen_card}")

            return self.card_effect(chosen_card, muted = muted)


    # Gives the probability that the specified player will be able to place a card on the discard stack with the knowledge about the discard_stack and the robots hand
    # This function will be used by the robot in move_score() to decide which move is a suitable move to make
    def chance_player_has_valid_card(self, player_id):
        if (not self.is_robot(player_id)):
            known_cards = self.discard_stack
            for i in range(self.num_players()):
                if (self.is_robot(i)):
                    known_cards += self.hands[i]

            # the counter preserves potential duplicate jokers in the deck
            unknown_cards_counter = Counter([(x.rank_id, x.suit_id) for x in standard_deck(2)]) - Counter([(x.rank_id, x.suit_id) for x in known_cards])
            unknown_cards = [PlayingCard(rank, suit) for (rank, suit) in unknown_cards_counter.elements()]

            valid_unknown_cards = [x for x in unknown_cards if self.is_valid_card(x)]
            
            chance_1_valid = float(len(valid_unknown_cards)) / len(unknown_cards) # chance 1 unknown card is valid
            chance_1_invalid = 1.0 - chance_1_valid # chance 1 unknown card is invalid
            chance_all_cards_invalid = chance_1_invalid ** self.number_of_cards(player_id) # chance that all cards in the players hand are invalid
        
            return 1.0 - chance_all_cards_invalid # chance that at least 1 valid card is in the players hand
        else:
            return 1.0 if len(self.valid_moves(player_id)) > 1 else 0.0


    # Gives a score to the resulting state after the current player_id (only used by the robot) makes the move
    # Used by the robot to decide which move is a suiting move to make 
    def move_score(self, robot_id, card_index):
        copy_state = copy.deepcopy(self)
        old_hand_size = copy_state.number_of_cards(robot_id)
        old_pestkaarten_sum = copy_state.pestkaarten_sum # The pestkaarten_sum value before the move is made
        old_top_card = copy_state.top_card() # The top card of the discard stack before the move is made

        # the 2 lines below make the move and if applicable advances the turn (so the score is calculated 1 turn in the future)
        if (copy_state.do_move(robot_id, card_index, muted=True)):
            copy_state.advance_turn()
            
        # TODO: experiment with this formula and weights

                # The number of cards in the hand of the player in the resulting gamestate
        score = (200 - 20 * len(copy_state.hands[robot_id]) \
                # The chance that the other player will be able to play a card in the resulting gamestate
                - 20 * copy_state.chance_player_has_valid_card(copy_state.turn) \
                # The difference between the number of cards in hand after making the move
                + (old_hand_size - copy_state.number_of_cards(robot_id)) \
                # Penalize for having no valid moves in the resulting gamestate
                - 10 * (0 if len(copy_state.valid_moves(robot_id)) > 1 else 1) \
                # Reward for again getting the next turn  in the resulting gamestate
                + 50 * (1 if copy_state.turn == robot_id else 0) \
                # If pestkaarten_sum is greater than zero before player has made its move, reward for playing a pestkaart.
                + 10 * (1 if old_pestkaarten_sum > 0 and copy_state.pestkaarten_sum > old_pestkaarten_sum else 0) \
                # Penalize for playing a pestkaart when pestkaarten_sum is not greater than zero before player has made its move 
                # and when next_player has relatively many cards left.
                - 10 * (1 if old_pestkaarten_sum <= 0 and copy_state.number_of_cards(copy_state.turn) > 4 else 0) \
                # small reward for playing a non-standard card
                + 5 * (1 if old_top_card != copy_state.top_card() and copy_state.top_card().rank_id in [0,1,2,7,8] else 0) \
                )
        return score


    # The return value is True if the game is over, False otherwise
    def robot_turn(self, difficulty):
        if (self.skip_next_turn):
            self.skip_next_turn = False
            print(f"Player {self.turn}'s turn is skipped.")
            return False

        print(f"It is player {self.turn}'s turn.")

        turn_over = False
        while not turn_over:
            print(f"Player {self.turn}'s hand: {self.hands[self.turn]}") # DEBUG

            # Obtains the list of valid moves
            valid_moves_lst = self.valid_moves(self.turn)
            print(f"valid_moves_lst: {valid_moves_lst}") # DEBUG

            # Obtains a list of scores for each valid move
            valid_moves_scores = [self.move_score(self.turn, move) for move in valid_moves_lst]
            print(f"valid_moves_scores: {valid_moves_scores}") # DEBUG

            valid_moves_probs = softmax_with_difficulty(valid_moves_scores, difficulty)
            print(f"valid_moves_probs: {valid_moves_probs}") # DEBUG

            # Randomly chooses a move weighted on the probabilities, chosen_move == -1 means drawing a card
            chosen_move = random.choices(valid_moves_lst, weights=valid_moves_probs)[0] 

            # The chosen move is made and turn_over is updated accordingly
            turn_over = self.do_move(self.turn, chosen_move)

            # Checks whether robot has won the game
            if (self.has_won(self.turn)):
                print(f"Player {self.turn} has won the game!")
                print(f"hands: {self.hands}") # DEBUG
                return True

        # Checks whether robot has won the game
        if (self.has_won(self.turn)):
            print(f"Player {self.turn} has won the game!")
            print(f"hands: {self.hands}") # DEBUG
            return True
        else:
            return False

    # The return value is True if the game is over, False otherwise
    def player_turn(self): 
        if (self.skip_next_turn):
            self.skip_next_turn = False
            print(f"Player {self.turn}'s turn is skipped.")
            return False

        print(f"It is player {self.turn}'s turn.")

        turn_over = False
        while not turn_over:
            print(f"Player {self.turn}'s hand: {self.hands[self.turn]}")
            print(f"The top card on the discard stack is {self.top_card()}.")

            if (0 < self.pestkaarten_sum):
                print(f"You need to throw a 'pestkaart' or you will be forced to draw {self.pestkaarten_sum} new cards.")

            print("Play a card or draw new card(s).")

            card = camera_detect_played_card()

            if isinstance(card, PlayingCard):
                if (not self.is_valid_card(card)):
                    print(f"Player {self.turn} played an invalid card: {card}. lmao")
                
                print(f"Player {self.turn} plays: {card}")
                self.hands[self.turn] -= 1
                self.discard_stack.insert(0, card)
                turn_over = self.card_effect(card)
                if (self.has_won(self.turn)):
                    print(f"Player {self.turn} has won the game!")
                    print(f"hands: {self.hands}") # DEBUG
                    return True     
                continue
            else:
                if (0 < self.pestkaarten_sum): # If the player must draw cards
                    if (card != self.pestkaarten_sum):
                        print(f"Player {self.turn} should have drawn {self.pestkaarten_sum} cards, but actually drew {card} cards. lmao")
                        
                    self.draw_cards(self.turn, card)
                    print(f"Player {self.turn} draws {card} cards.")
                    self.pestkaarten_sum = 0
                    continue # The player must still play after drawing the forced cards
                else:
                    self.draw_cards(self.turn, amount=1)
                    turn_over = True
                    continue # Drawing a card by choice, ends the turn

        # Checks whether player has won the game after the turn is over
        if (self.has_won(self.turn)):
            print(f"Player {self.turn} has won the game!")
            print(f"hands: {self.hands}") # DEBUG
            return True
        else:
            return False

    # returns the player_id of the winner, or -1 if the game is not yet over
    def do_turn(self, difficulty):
        if self.is_robot(self.turn):
            game_done = self.robot_turn(difficulty) # the robot takes its turn
            if game_done: # If the function robot_turn returns true, the robot has won the game
                return self.turn
        else: # Else, it is the turn of a player
            game_done = self.player_turn()
            if game_done:
                return self.turn # If the function player_turn() returns true, the player has won the game

        self.advance_turn()
        return -1 # If the function returns -1, the game is not yet over

# completes on full game until someone wins
def do_game(gamestate, difficulty):
    while True:
        print(gamestate) # DEBUG
        turnresult = gamestate.do_turn(difficulty)
        if (0 <= turnresult):
            return turnresult


def playsession(is_robot_list, difficulty, player_total_wins = 0.0, robot_total_wins = 0.0):
    gamestate = Pesten_Unknown_GameState()
    
    while True:
        gamestate.setup(is_robot_list)
        print(gamestate) # DEBUG
        print(f"Player wins: {player_total_wins}, Robot wins: {robot_total_wins}, win ratio: {player_total_wins/(player_total_wins+robot_total_wins) if (player_total_wins+robot_total_wins) > 0 else 0}")
        print(f"Current difficulty: {difficulty}")
        
        winner = gamestate.do_game(difficulty)
        if (is_robot_list[winner]):
            robot_total_wins += 1
        else:
            player_total_wins += 1

        
        


def main():
    gamestate = Pesten_Unknown_GameState()
    gamestate.setup([True, False, False])
    # print(gamestate)

    do_game(gamestate, 1.0)
    # playsession([True, False, False], 1.0) # WARNING INFINITE LOOP
    

if __name__ == "__main__":
    main()



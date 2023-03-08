import random
import numpy as np
from playing_cards_classes import Pesten_GameState

gamestate = Pesten_GameState() # global state of the gamestate

# Converts arbitrary scores to probabilities using a modified softmax function
# If difficulty = 0, the function returns a uniform probability for all scores 
# If 0 < difficulty < 1, the function gives a higher probability to the highest score 
# If difficulty = 1, the function gives approximately a probability of ~1 to the highest score, and ~0 to all other scores
def softmax_with_difficulty(scores, diff):
    b_x = np.power(1.0 + (diff ** 3), scores - np.max(scores)) # Note to self: the power of the difficulty (>= 1) can be played with to change relative probabilities
    return b_x / b_x.sum()


# The return value is True if the game is over, False otherwise
def robot_turn(difficulty):
    if (gamestate.skip_next_turn):
        gamestate.skip_next_turn = False
        print(f"Player {gamestate.turn}'s turn is skipped.")
        return False

    print(f"It is player {gamestate.turn}'s turn.")

    turn_over = False
    while not turn_over:
        print(f"Player {gamestate.turn}'s hand: {gamestate.hands[gamestate.turn]}") # DEBUG

        # Obtains the list of valid moves
        valid_moves_scores = []
        valid_moves_lst = gamestate.valid_moves(gamestate.turn)
        print(f"valid_moves_lst: {valid_moves_lst}") # DEBUG

        # Obtains a list of scores for each valid move
        for move in valid_moves_lst:
            valid_moves_scores.append(gamestate.move_score(0, move))
        print(f"valid_moves_scores: {valid_moves_scores}") # DEBUG

        valid_moves_probs = softmax_with_difficulty(valid_moves_scores, difficulty)
        print(f"valid_moves_probs: {valid_moves_probs}") # DEBUG

        # Randomly chooses a move weighted on the probabilities, chosen_move == -1 means drawing a card
        chosen_move = random.choices(valid_moves_lst, weights=valid_moves_probs)[0] 

        # The chosen move is made and turn_over is updated accordingly
        turn_over = gamestate.play_card(gamestate.turn, chosen_move)

        # Checks whether robot has won the game
        if (gamestate.has_won(gamestate.turn)):
            print("Player {gamestate.turn} has won the game!")
            print("hands = " + str(gamestate.hands)) # DEBUG
            return True

    # Checks whether robot has won the game
    if (gamestate.has_won(gamestate.turn)):
        print(f"Player {gamestate.turn} has won the game!")
        print("hands = " + str(gamestate.hands)) # DEBUG
        return True
    else:
        return False

# The return value is True if the game is over, False otherwise
def player_turn(): 
    if (gamestate.skip_next_turn):
        gamestate.skip_next_turn = False
        print(f"Player {gamestate.turn}'s turn is skipped.")
        return False

    print(f"It is player {gamestate.turn}'s turn.")

    turn_over = False
    while not turn_over:
        print(f"Player {gamestate.turn}'s hand: {gamestate.hands[gamestate.turn]}")
        print(f"The current card on the discard stack: {gamestate.top_card()}")

        # Obtain the list of valid moves
        valid_moves_lst = gamestate.valid_moves(gamestate.turn)

        if (0 < gamestate.pestkaarten_sum):
            print(f"You need to throw a 'pestkaart' or you will be forced to draw {gamestate.pestkaarten_sum} new cards.")

            if len(valid_moves_lst) <= 1: # If player has at most one option, the player can only draw a card
                print("You have no 'pestkaart'.")
                turn_over = gamestate.play_card(gamestate.turn, -1)
                continue

        # The player is given the choice to play a card or draw a cards each turn
        response = input("Type a card to play or 'Draw' to take new cards: ")

        if ((0 < len(response)) and response.lower()[0] == 'd'): # Player chooses to draw a card
            turn_over = gamestate.play_card(gamestate.turn, -1)
            continue
        else:
            selected_card = None
            for playing_card in gamestate.hands[gamestate.turn]:
                if response.upper() == playing_card.short_name():
                    selected_card = playing_card

            if selected_card == None:
                print("You don't have that card. Try again.")
                continue # Again, give the player the option to choose between playing a card or drawing a card
            else:
                if selected_card in valid_moves_lst:
                    turn_over = gamestate.play_card(gamestate.turn, gamestate.hands[gamestate.turn].index(selected_card))
                    # Checks whether player has won the game
                    if (gamestate.has_won(gamestate.turn)):
                        print("Player {gamestate.turn} has won the game!")
                        print("hands = " + str(gamestate.hands)) # DEBUG
                        return True
                else:
                    print("This is not a valid move. Try again.")
                    continue # Again, give the player the option to choose between playing a card or drawing a card
                
    # Checks whether player has won the game
    if (gamestate.has_won(gamestate.turn)):
        print(f"Player {gamestate.turn} has won the game!")
        print("hands = " + str(gamestate.hands)) # DEBUG
        return True
    else:
        return False


def playsession():
    player_total_wins = 0
    robot_total_wins = 0

    # TODO: make difficulty change over time after each game or move
    difficulty = float(input("Enter a starting difficulty level between 0 and 1 (inclusive): "))

    number_of_players = int(input("Enter the number of players (including robot >= 2): "))
    assert number_of_players >= 2, "not enough players"
    
    playsession_done = False
    
    while not playsession_done:
        gamestate.setup(player_count=number_of_players) # Resets the gamestate: creates a new deck and deals 7 cards to each player, a random player gets the turn

        print("starting gamestate:")
        print(gamestate) # DEBUG
        print(f"Difficulty level: {difficulty}")

        game_done = False
        while not game_done:
            print()
            if gamestate.turn == 0:
                if robot_turn(difficulty):
                    robot_total_wins += 1
            else:
                if player_turn():
                    player_total_wins += 1

            gamestate.advance_turn()

        play_again = input("Play again (Yes/No)? ")
        if (0 < len(play_again) and play_again.lower()[0] == 'y'):
            print(f"\nSo far, you have won {player_total_wins} games")
            print(f" and the robot has won {robot_total_wins} games.")
            game_done = False
        else:
            playsession_done = True

    print("\nFinal score:")
    print(f"Number of games won by you: {player_total_wins}   Number of games won by the robot: {robot_total_wins}")
    print(f" win/loss ratio is {player_total_wins / (player_total_wins + robot_total_wins) if (player_total_wins + robot_total_wins) > 0 else 0}")


if __name__ == "__main__":
    # print(softmax_with_difficulty(np.array([50,30,20]), 0))
    # print(softmax_with_difficulty(np.array([50,30,20]), 0.5))
    # print(softmax_with_difficulty(np.array([50,30,20]), 1.0))
    playsession()
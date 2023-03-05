import random
import numpy as np
from playing_cards_classes import Pesten_GameState, suit_to_str

game = Pesten_GameState() # global state of the game


def choose_new_suit():
    chosen_suit = 0
    while (chosen_suit == 0):
        suit = input("Pick a suit (Diamonds/Hearts/Spades/Clubs): ")
        if (0 == len(suit)):
            print("Not a valid suit. Try again.")
        if suit.lower()[0] == 'd':
            chosen_suit = 1
        elif suit.lower()[0] == 'h':
            chosen_suit = 2
        elif suit.lower()[0] == 's':
            chosen_suit = 3
        elif suit.lower()[0] == 'c':
            chosen_suit = 4
        else:
            print("Not a valid suit. Try again.")
    print(f"You picked {suit_to_str(chosen_suit)}")
    return chosen_suit

# Gives a score to the resulting state after the current player plays the given card
# Used by the robot to decide which move is best
# TODO: does not allow voluntary drawing a card
def state_score(game, playing_card): # TODO: implement this function
    return 1

# returns the score of the game after choosing a specified new suit using the Jack (this is the playing card)
def suit_score(game, playing_card, new_suit): # TODO: implement
    return 1

# Converts arbitrary scores to probabilities using a modified softmax function
# If difficulty = 0, the function returns a uniform probability for all scores 
# If 0 < difficulty < 1, the function gives a higher probability to the highest score 
# If difficulty = 1, the function gives approximately a probability of ~1 to the highest score, and ~0 to all other scores
def softmax_with_difficulty(scores, diff):
    b_x = np.power(1.0 + (diff ** 3), scores - np.max(scores)) # Note to self: the power of the difficulty (>= 1) can be played with to change relative probabilities
    return b_x / b_x.sum()

def robot_turn(difficulty):
    if (game.skip_next_turn):
        game.skip_next_turn = False
        print(f"Player {game.turn}'s turn is skipped.")
        return False

    print(f"It is the robot's turn.")

    turn_over = False
    while not turn_over:
        valid_moves_lst = []
        valid_moves_scores = []

        print(f"Robot's hand: {game.hands[game.turn]}") # DEBUG

        if (0 < game.pestkaarten_sum): # the robot needs to play a pestkaart (or draw)
            for playing_card in game.hands[game.turn]:
                if (playing_card.rank_id in [0,2]): # assumes the rank 2 pestkaart can always be played on top of another pestkaart
                    valid_moves_lst.append(playing_card)
                    valid_moves_scores.append(state_score(game, playing_card))
        elif (game.top_card().rank_id == 11): 
            for playing_card in game.hands[game.turn]:
                if ((playing_card.suit_id in [0, game.active_suit]) or (playing_card.rank_id == game.top_card().rank_id)):
                    valid_moves_lst.append(playing_card)
                    valid_moves_scores.append(state_score(game, playing_card))
        else:
            for playing_card in game.hands[game.turn]:
                if ((playing_card.suit_id in [0, game.top_card().suit_id]) or (playing_card.rank_id == game.top_card().rank_id) or (game.top_card().suit_id == 0)):
                    valid_moves_lst.append(playing_card)
                    valid_moves_scores.append(state_score(game, playing_card))


        if len(valid_moves_lst) == 0:
            if (0 < game.pestkaarten_sum):
                print(f"Player {game.turn} draws {game.pestkaarten_sum} cards.")
                game.draw_cards(game.turn, game.pestkaarten_sum)
                game.pestkaarten_sum = 0
                continue
            else:
                game.draw_card(game.turn)
                print(f"Player {game.turn} draws 1 card.")
                turn_over = True
                continue
        else: # TODO: currently only plays the best possible move, but should vary based on difficulty
            print(f"valid_moves_lst: {valid_moves_lst}") # DEBUG
            valid_moves_probs = softmax_with_difficulty(valid_moves_scores, difficulty)
            print(f"valid_moves_probs: {valid_moves_probs}") # DEBUG
            chosen_move = random.choices(valid_moves_lst, weights=valid_moves_probs)[0] # randomly chooses a move weighted on the probabilities

            game.play_card(game.turn, game.hands[game.turn].index(chosen_move))
            print(f"Player {game.turn} plays {chosen_move}")
            turn_over = True
            if (chosen_move.rank_id in [0,2]):
                game.pestkaarten_sum += (5 if chosen_move.rank_id == 0 else 2)
                
                print(f"the next player needs to draw {game.pestkaarten_sum} new cards.")
            elif (chosen_move.rank_id == 7):
                if (len(game.hands[game.turn]) == 0): # We check if the hand is empty before the player takes another turn.
                    print("The robot has played all cards in their hand. It wins!")
                    # Print the playing cards the robot had left to play with.
                    print(f"The player had these playing card(s) left: {game.hands[1]}")
                    return True
                print(f"Player {game.turn} takes another turn.")
                turn_over = False
                continue
            elif (chosen_move.rank_id == 8):
                print(f"The next player is forced to skip their turn.")
                game.skip_next_turn = True
                continue
            elif (chosen_move.rank_id == 11):
                suit_scores = [0.0] # pre-filled with an item to make the indexing easier
                for suit in range(1, 4+1): 
                    suit_scores.append(suit_score(game, chosen_move, suit))
                
                print(f"suit_scores: {suit_scores}") # DEBUG
                suit_scores_probs = softmax_with_difficulty(suit_scores, difficulty)
                print(f"suit_scores_probs: {suit_scores_probs}") # DEBUG

                game.active_suit = random.choices(list(range(1, 4+1)), weights=suit_scores_probs)[0] # randomly chooses a suit weighted on the probabilities
                print(f"Player {game.turn} has chosen the active suit to be: {suit_to_str(game.active_suit)}.")
                continue

        # if a == True:
        #     if pestkaart_in_robot_hand == True:
        #         playing_card_to_discard = pestkaarten_robot[0]
        #         robot_hand.remove(playing_card_to_discard)
        #         discard_stack.append(playing_card_to_discard)
        #         print("  Robot played " + playing_card_to_discard.short_name)
        #     else:
        #         for playing_card in range(0, pestkaarten_sum):
        #             if len(playing_stack) > 0:
        #                 new_playing_card_robot = random.choice(playing_stack)
        #                 robot_hand.append(new_playing_card_robot)
        #                 playing_stack.remove(new_playing_card_robot)
        #                 print("  Robot drew a card.")
        #             else: 
        #                 blocked = blocked + 1
        #                 print("All cards from the playing stack have been taken, robot cannot obtain new card.")
        #             # After drawing cards, it the turn for the robot again.
        #             a = False
        #             robot_turn()
        # else: 
        #     if len(valid_moves) > 0 and a == False:

        #         # TODO: create algorithm that uses probability in order to obtain the optimal play to make here
        #         # TODO: It should use the knowledge about the cards that are already on the discard_stack
        #         #optimal_play = valid_moves[0]
        #         #for playing_card in valid_moves:
        #         #    if playing_card.value > optimal_play.value:
        #         #        optimal_play = playing_card
                    
        #         playing_card_to_discard = valid_moves[0]
        #         robot_hand.remove(playing_card_to_discard)
        #         discard_stack.append(playing_card_to_discard)
        #         print("  Robot played " + playing_card_to_discard.short_name)
        #         # If the playing card that is thrown on the discard stack is a 7 or 8, the robot again gets the next turn.
        #         if playing_card_to_discard.rank == "7" or playing_card_to_discard.rank == "8":
        #             robot_turn()
        #         # If the playing cards that is thrown on the discard stack is 2 or 14, the player either needs to throw a "pestkaart" or needs to take new cards.
        #         elif (playing_card_to_discard.rank == "2" or playing_card_to_discard.rank == "0") and a == True:
        #             pestkaarten_sum = pestkaarten_sum + playing_card_to_discard.rank
        #             a = True
        #     else:
        #         # If the robot has a jack, we put a jack on the discard stack and choose the suit for which we have the most playing cards.
        #         if jack_in_robot_hand == True:
        #             playing_card_to_discard = jacks_robot[0]
        #             robot_hand.remove(playing_card_to_discard)
        #             discard_stack.append(playing_card_to_discard)
        #             print("  Robot played " + playing_card_to_discard.short_name)
        #             # suit_totals = [diamonds, spades, hearts, clubs]
        #             suit_totals = [0, 0, 0, 0]
        #             for suit in range(1, 5):
        #                 for card in robot_hand:
        #                     if card.suit_id == suit:
        #                         suit_totals[suit - 1] += 1
        #             long_suit = 0
        #             for i in range(4):
        #                 if suit_totals[i] > long_suit:
        #                     long_suit = i
        #             if long_suit == 0:
        #                 active_suit = "Diamonds"
        #             elif long_suit == 1:
        #                 active_suit = "Hearts"
        #             elif long_suit == 2:
        #                 active_suit = "Spades"
        #             elif long_suit == 3:
        #                 active_suit = "Clubs"
        #             print("  Computer changed suit to" + active_suit)
        #         else: # No options for the robot, so it needs to take a new card from the playing_stack
        #             if len(playing_stack) > 0:
        #                 new_playing_card_robot = random.choice(playing_stack)
        #                 robot_hand.append(new_playing_card_robot)
        #                 playing_stack.remove(new_playing_card_robot)
        #                 print("  Robot drew a card.")
        #             else: 
        #                 blocked = blocked + 1
        #                 print("All cards from the playing stack have been taken, robot cannot obtain new card.")

    if (len(game.hands[game.turn]) == 0):
        print("The robot has played all cards in their hand. It wins!")
        # Print the playing cards the robot had left to play with.
        print(f"The player had these playing card(s) left: {game.hands[1]}")
        return True
    else:
        return False



def player_turn(): # return value is True if the game is over, False otherwise
    if (game.skip_next_turn):
        game.skip_next_turn = False
        print(f"Player {game.turn}'s turn is skipped.")
        return False

    print(f"It is player {game.turn}'s turn.")
    turn_over = False
    while not turn_over:
        print(f"Your hand: {game.hands[game.turn]}")
        print(f"The current card on the discard stack: {game.top_card()}")

        if (game.top_card().rank_id == 11):
            print(f"The current active suit that was chosen is: {suit_to_str(game.active_suit)}")
        if (game.top_card().rank_id in [0, 2] and 0 < game.pestkaarten_sum):
            print(f"The current card on the discard stack is a 'pestkaart'. You need to throw a 'pestkaart' too or you will be forced to draw {game.pestkaarten_sum} new cards!")
            has_pestkaart = False
            for playing_card in game.hands[game.turn]:
                if playing_card.rank_id in [0, 2]:
                    has_pestkaart = True
            if not has_pestkaart:
                print(f"You don't have a 'pestkaart' in your hand. You are forced to draw {game.pestkaarten_sum} cards.")
                game.draw_cards(game.turn, game.pestkaarten_sum)
                game.pestkaarten_sum = 0


        response = input("Type a card to play or 'Draw' to take new cards: ")

        if ((0 < len(response)) and response.lower()[0] == 'd'): # TODO: player is allowed to draw when there is a pestkaart on the discard stack???
            if (0 < game.pestkaarten_sum):
                print(f"You chose to draw {game.pestkaarten_sum} new cards.")
                game.draw_cards(game.turn, game.pestkaarten_sum)
                game.pestkaarten_sum = 0
                continue
            else:
                game.draw_card(game.turn)
                print("Player drew a card.")
                turn_over = True
                continue
        else:
            selected_card = None
            for playing_card in game.hands[game.turn]:
                if response.upper() == playing_card.short_name():
                    selected_card = playing_card
            if selected_card == None:
                print("You don't have that card. Try again.")
                continue

        if (selected_card.rank_id in [0, 2]):
            game.play_card(game.turn, game.hands[game.turn].index(selected_card))
            game.pestkaarten_sum += (5 if selected_card.rank_id == 0 else 2)
            turn_over = True
            print(f"You played {selected_card.short_name()}")
            print(f"the next player needs to draw {game.pestkaarten_sum} new cards.")
        elif ((game.top_card().rank_id in [0, 2]) and (0 < game.pestkaarten_sum) and not (selected_card.rank_id in [0, 2])):
            print("Either play a 'pestkaart' or draw. Try again: ")
            continue
        elif ((selected_card.suit_id in [0, (game.top_card().suit_id if (game.top_card().rank_id != 11) else game.active_suit)] ) or (selected_card.rank_id == game.top_card().rank_id) or (game.top_card().suit_id == 0)):
            game.play_card(game.turn, game.hands[game.turn].index(selected_card))
            print(f"You played {selected_card.short_name()}")
            turn_over = True
            if (selected_card.rank_id == 7):
                if (len(game.hands[game.turn]) == 0): # We check if the hand is empty before the player takes another turn.
                    print("You have played all cards in your hand. You won!")
                    # Print the playing cards the robot had left to play with.
                    print(f"The robot had these playing card(s) left: {game.hands[0]}")
                    return True
                turn_over = False
                print("You take another turn.")
                continue
            elif (selected_card.rank_id == 8):
                print("The next player is forced to skip their turn.")
                game.skip_next_turn = True
                continue
            elif (selected_card.rank_id == 11):
                game.active_suit = choose_new_suit()
                continue
        else:
            print("You cannot play that card. Try again.")
            continue

    if (len(game.hands[game.turn]) == 0):
        print("You have played all cards in your hand. You won!")
        # Print the playing cards the robot had left to play with.
        print(f"The robot had these playing card(s) left: {game.hands[0]}")
        return True
    else:
        return False






def main():
    player_total_wins = 0
    robot_total_wins = 0

    # TODO: make difficulty change over time after each game or move
    difficulty = float(input("Enter a starting difficulty level between 0 and 1 (inclusive): "))
    
    
    done = False
    game_done = False
    while not done:
        #blocked = 0
        game.setup(player_count=2) # resets the game: creates a new deck, shuffles it, and deals 7 cards to each player, a random player starts the turn

        print("starting game:")
        print(game) # TODO: comment this line before submission
        print(f"Difficulty level: {difficulty}")

        while not game_done:
            print()
            if game.turn == 0:
                game_done = robot_turn(difficulty)
                if game_done:
                    robot_total_wins += 1
            else:
                game_done = player_turn()
                if game_done:
                    player_total_wins += 1
            game.turn = (game.turn + 1) % game.num_players()

            # if blocked >= 2:
            #     game_done = True
            #     print("Both players blocked. GAME OVER.")
            #     print(f"The robot had these playing card(s) left: {game.hands[0]}")
            #     print(f"You had these playing card(s) left: {game.hands[1]}")
        play_again = input("Play again (Yes/No)? ")
        if (0 < len(play_again) and play_again.lower()[0] == 'y'):
            print(f"\nSo far, you have won {player_total_wins} game(s)")
            print(f" and the robot has won {robot_total_wins} game(s).")
            game_done = False
        else:
            done = True

    print("\nFinal score:")
    print(f"Number of games won by you: {player_total_wins}   Number of games won by the robot: {robot_total_wins}")
    print(f" win/loss ratio is {player_total_wins / (player_total_wins + robot_total_wins) if (player_total_wins + robot_total_wins) > 0 else 0}")


if __name__ == "__main__":
    # print(softmax_with_difficulty(np.array([50,30,20]), 0))
    # print(softmax_with_difficulty(np.array([50,30,20]), 0.5))
    # print(softmax_with_difficulty(np.array([50,30,20]), 1.0))

    main()
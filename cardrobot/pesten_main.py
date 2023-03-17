import os
import random
import numpy as np
import threading
from PIL import Image, ImageTk
from tkinter import Frame, LabelFrame
from tkinter import Text
from tkinter import Label
from tkinter import Tk
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
        update_gamestate_status_user_interface(f"Player {gamestate.turn}'s turn is skipped.")
        print(f"Player {gamestate.turn}'s turn is skipped.")
        return False
    
    update_gamestate_status_user_interface(f"It is player {gamestate.turn}'s turn.")
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
        update_user_interface(gamestate.discard_stack[0]) # robot made a play, update GUI

        # Checks whether robot has won the game
        if (gamestate.has_won(gamestate.turn)):
            update_gamestate_status_user_interface(f"Player {gamestate.turn} has won the game!")
            print(f"Player {gamestate.turn} has won the game!")
            print("hands = " + str(gamestate.hands)) # DEBUG
            return True

    # Checks whether robot has won the game
    if (gamestate.has_won(gamestate.turn)):
        update_gamestate_status_user_interface(f"Player {gamestate.turn} has won the game!")
        print(f"Player {gamestate.turn} has won the game!")
        print("hands = " + str(gamestate.hands)) # DEBUG
        return True
    else:
        return False

# The return value is True if the game is over, False otherwise
def player_turn(): 
    if (gamestate.skip_next_turn):
        gamestate.skip_next_turn = False
        update_gamestate_status_user_interface(f"Player {gamestate.turn}'s turn is skipped.")
        print(f"Player {gamestate.turn}'s turn is skipped.")
        return False
    
    update_text_gui_extra("The play direction is now clockwise.")
    update_gamestate_status_user_interface(f"It is player {gamestate.turn}'s turn.")
    print(f"It is player {gamestate.turn}'s turn.")

    turn_over = False
    while not turn_over:
        print(f"Player {gamestate.turn}'s hand: {gamestate.hands[gamestate.turn]}")
        print(f"The top card on the discard stack is {gamestate.top_card()}.")

        if (0 < gamestate.pestkaarten_sum):
            update_gamestate_status_user_interface(f"You need to throw a 'pestkaart' or you will be forced to draw {gamestate.pestkaarten_sum} new cards.")
            print(f"You need to throw a 'pestkaart' or you will be forced to draw {gamestate.pestkaarten_sum} new cards.")

        # The player is given the choice to play a card or draw a cards each turn
        response = input("Type a card to play or 'Draw' to take new cards: ")

        if ((0 < len(response)) and (response.lower()[0] == 'd')): # Player chooses to draw a card
            turn_over = gamestate.play_card(gamestate.turn, -1)
            continue
        else: # Player chose to play a card

            try:
                selected_move = [x.short_name() for x in gamestate.hands[gamestate.turn]].index(response.upper())
            except ValueError:
                print("You don't have that card. Try again.")
                continue # Again, give the player the option to choose between playing a card or drawing a card

            if (gamestate.is_valid_card(gamestate.hands[gamestate.turn][selected_move])): 
                turn_over = gamestate.play_card(gamestate.turn, selected_move)
                update_user_interface(gamestate.discard_stack[0]) # player made a play, update GUI
                # Checks whether player has won the game
                if (gamestate.has_won(gamestate.turn)):
                    update_gamestate_status_user_interface(f"Player {gamestate.turn} has won the game!")
                    print(f"Player {gamestate.turn} has won the game!")
                    print("hands = " + str(gamestate.hands)) # DEBUG
                    return True     
            else: 
                print("This card is not a valid move. Try again.")
                continue # Again, give the player the option to choose between playing a card or drawing a card
                      
                
    # Checks whether player has won the game after the turn is over
    if (gamestate.has_won(gamestate.turn)):
        update_gamestate_status_user_interface(f"Player {gamestate.turn} has won the game!")
        print(f"Player {gamestate.turn} has won the game!")
        print("hands = " + str(gamestate.hands)) # DEBUG
        return True
    else:
        return False

# Function to resize the playing card images
def resize_playing_card_images(playing_card):
    # Open the image
    original_playing_card_image = Image.open(playing_card)

    # Resize the image
    playing_card_image = original_playing_card_image.resize((150, 220))

    # Obtain the resized image
    global resize_playing_card_image
    resize_playing_card_image = ImageTk.PhotoImage(playing_card_image)

    # Return the resized image
    return resize_playing_card_image

# Update the draw or discard stack depending on what play was made
def update_user_interface(top_card):
    file_path_image_1 = os.path.abspath("cardrobot/Playing cards/back of playing card.png")

    original_playing_card_1_image = Image.open(file_path_image_1).resize((150,220))
    global resize_playing_card_1_image
    resize_playing_card_1_image = ImageTk.PhotoImage(original_playing_card_1_image)
    
    draw_stack_label.config(image = resize_playing_card_1_image)
    file_path_image_2 = os.path.abspath(f"cardrobot/Playing cards/{top_card}.png")

    original_playing_card_2_image = Image.open(file_path_image_2).resize((150,220))
    global resize_playing_card_2_image
    resize_playing_card_2_image = ImageTk.PhotoImage(original_playing_card_2_image)

    discard_stack_label.config(image = resize_playing_card_2_image) # The top card on the discard stack  

# Updates text widget which shows the current action robot is performing / an instruction for the player
def update_gamestate_status_user_interface(string):
    text_widget.config(text=string)

def update_text_gui_extra(string):
    text_widget_extra.config(text=string)

def graphical_user_interface():
    root = Tk()
    root.title("A game of Pesten")
    # Sets the icon of the window
    #root.iconbitmap()
    root.geometry("900x500")
    root.configure(background="green")

    # Create the top frame, containing the cards
    top_frame = Frame(root, background = "green")

    # Create the bottom frame, containing the text widget
    bottom_frame = Frame(root, background = "purple")

    # Layout of the two frames inside root
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1) 

    top_frame.grid(row=0, column=0, columnspan=2)
    bottom_frame.grid(row=1, column=0, columnspan=2)

    # Create the frames for the two game stacks and the two hands
    draw_stack_frame = LabelFrame(top_frame, text="Draw stack", font = ("Arial", 12), border=0)
    draw_stack_frame.grid(row=0, column=2, padx=20, pady=40, ipadx=20)

    discard_stack_frame = LabelFrame(top_frame, text="Discard stack", font = ("Arial", 12), border=0)
    discard_stack_frame.grid(row=0, column=3, padx=20, pady=40, ipadx=20) 

    # Create the frame for the text widget
    user_information_widget = LabelFrame(bottom_frame, text="", border=0)
    user_information_widget.pack()

    # Put cards in the frames, this is done by putting images into labels
    global draw_stack_label 
    draw_stack_label = Label(draw_stack_frame, text="")
    draw_stack_label.pack(pady=20)

    global discard_stack_label 
    discard_stack_label = Label(discard_stack_frame, text="")
    discard_stack_label.pack(pady=20)

    # Create label for the text widget
    text_widget_label = Label(user_information_widget, text="The current game status:")
    text_widget_label.pack()
    text_widget_label.config(font = ("Arial", 12)) # specify font

    # Create the text widget 
    global text_widget
    text_widget = Label(user_information_widget, height = 2, width = 80, text="") 
    text_widget.config(text="")
    text_widget.pack()

    global text_widget_extra
    text_widget_extra = Label(user_information_widget, height = 2, width = 80, text="") 
    text_widget_extra.config(text="")
    text_widget_extra.pack()

    # Call event loop which makes the window appear
    root.mainloop()

def playsession():

    player_total_wins = 0
    robot_total_wins = 0

    # TODO: make difficulty change over time after each game or move
    difficulty = float(input("Enter a starting difficulty level between 0 and 1 (inclusive): "))
    assert 0.0 <= difficulty <= 1.0, "difficulty level must be between 0 and 1 (inclusive)"

    number_of_players = int(input("Enter the number of players (including robot >= 2): "))
    assert number_of_players >= 2, "not enough players"
    
    playsession_done = False
    while not playsession_done:
        gamestate.setup(player_count=number_of_players) # Resets the gamestate: creates a new deck and deals 7 cards to each player, a random player gets the turn

        # Game is started, so GUI is updated 
        update_user_interface(gamestate.discard_stack[0])

        print("starting gamestate:")
        print(gamestate) # DEBUG
        print(f"Difficulty level: {difficulty}")

        update_gamestate_status_user_interface(f"The direction of play is {'clockwise' if gamestate.play_direction == 1 else 'anti-clockwise'}.")
        print(f"The direction of play is {'clockwise' if gamestate.play_direction == 1 else 'anti-clockwise'}.")

        game_done = False
        while not game_done:
            print()
            if gamestate.turn == 0: # Currently player 0 is hardcoded to be the robot
                game_done = robot_turn(difficulty) # the robot takes its turn
                if game_done: # If the function robot_turn returns true, the robot has won the game
                    robot_total_wins += 1
            else: # Else, it is the turn of a player
                game_done = player_turn()
                if game_done:
                    player_total_wins += 1 # If the function player_turn() returns true, the player has won the game

            gamestate.advance_turn()

        play_again = input("Play again (Yes/No)? ")
        if (0 < len(play_again) and play_again.lower()[0] == 'y'):
            update_gamestate_status_user_interface(f"\nSo far, you have won {player_total_wins} games and the robot has won {robot_total_wins} games.")
            print(f"\nSo far, you have won {player_total_wins} games")
            print(f" and the robot has won {robot_total_wins} games.")
            continue
        else:
            playsession_done = True

    print("\nFinal score:")
    print(f"Number of games won by you: {player_total_wins}   Number of games won by the robot: {robot_total_wins}")
    print(f" win/loss ratio is {player_total_wins / (player_total_wins + robot_total_wins) if (player_total_wins + robot_total_wins) > 0 else 0}")    

if __name__ == "__main__":
    # print(softmax_with_difficulty(np.array([50,30,20]), 0))
    # print(softmax_with_difficulty(np.array([50,30,20]), 0.5))
    # print(softmax_with_difficulty(np.array([50,30,20]), 1.0))

    GUI_thread = threading.Thread(target=graphical_user_interface)
    GUI_thread.start()
    playsession()
    GUI_thread.join()
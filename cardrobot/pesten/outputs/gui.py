import time
from game.output import GameOutput
from pesten.types import PestenOutputType
from pesten.player import PestenPlayer
from pesten.state import PestenGameState
from PIL import Image, ImageTk
from tkinter import Button, Frame, LabelFrame, PhotoImage, Scrollbar, Text, Toplevel
from tkinter import Label
from tkinter import Tk
import os
import threading

class GUIOutput(GameOutput):
    state: PestenGameState
    thread: threading.Thread

    # Tkinter variables
    root: Tk
    draw_stack_label: Label
    discard_stack_label: Label
    text_widget_turn: Label
    text_widget_extra: Label
    resize_playing_card_1_image: ImageTk.PhotoImage
    resize_playing_card_2_image: ImageTk.PhotoImage

    def __init__(self, state):
        super().__init__(state)

        self.register(PestenOutputType.PLAYER_TURN, self.player_turn)
        self.register(PestenOutputType.PLAYER_DRAWS, self.player_draws)
        self.register(PestenOutputType.PLAYER_PLAYS, self.player_plays)
        self.register(PestenOutputType.PLAYER_WON, self.player_won)
        self.register(PestenOutputType.EFFECT_DRAW_CARDS, self.effect_draw_cards)
        self.register(PestenOutputType.EFFECT_REVERSE_DIRECTION, self.effect_reverse_direction)
        self.register(PestenOutputType.EFFECT_EXTRA_TURN, self.effect_extra_turn)
        self.register(PestenOutputType.EFFECT_SKIP_TURN, self.effect_skip_turn)

        self.thread = threading.Thread(target=self.init_ui)
        self.thread.daemon = True # Stop thread when main thread stops
        self.thread.start()

    def init_ui(self):
        self.root = Tk()
        self.root.title("A game of Pesten")

        # Sets the icon of the window
        self.root.iconbitmap("cardrobot/Other images/App icon.ico")

        self.root.geometry("900x600")
        self.root.configure(background="green")

        # Create the top frame, containing the cards
        top_frame = Frame(self.root, background = "green")

        # Create the bottom frame, containing the text widget
        bottom_frame = Frame(self.root, background = "green")

        # Layout of the two frames inside root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) 

        top_frame.grid(row=0, column=0, columnspan=2)
        bottom_frame.grid(row=1, column=0, columnspan=2)
        
        # Create the frames for the two game stacks and the two hands
        draw_stack_frame = LabelFrame(top_frame, text="Draw stack", font = ("Arial", 14, 'bold'), border=0)
        draw_stack_frame.grid(row=0, column=2, padx=20, pady=40, ipadx=20)

        discard_stack_frame = LabelFrame(top_frame, text="Discard stack", font = ("Arial", 14, 'bold'), border=0)
        discard_stack_frame.grid(row=0, column=4, padx=20, pady=40, ipadx=20)

        # Put cards in the frames, this is done by putting images into labels
        self.draw_stack_label = Label(draw_stack_frame, text="")
        self.draw_stack_label.pack(pady=20)

        self.discard_stack_label = Label(discard_stack_frame, text="")
        self.discard_stack_label.pack(pady=20)

        # Create the frame for the text widgets
        game_information_frame = LabelFrame(bottom_frame, text="", border=0)
        #game_information_frame.grid_rowconfigure(3, minsize=2) # Set size of row 3 to standard height of 2, row 3 is empty
        game_information_frame.pack()

        # Create label for the game status header text widget
        self.text_widget_label = Label(game_information_frame, text="The current game status:")
        self.text_widget_label.grid(row=1) # pack()
        self.text_widget_label.config(font = ("Arial", 14, 'bold')) # specify font

        # Create the game status text widget labels
        self.text_widget_turn = Label(game_information_frame, height = 2, width = 90) 
        self.text_widget_turn.config(text="", font = ("Arial", 12))
        self.text_widget_turn.grid(row=2) # pack()

        self.text_widget_extra = Label(game_information_frame, height = 2, width = 90) 
        self.text_widget_extra.config(text="", font = ("Arial", 12))
        self.text_widget_extra.grid(row=4) # pack()

        # Add empty row with background color green between game status information and robot'status information
        self.empty_row = Label(game_information_frame, background = "green", height = 2, width = 90) 
        self.empty_row.config(text="", font = ("Arial", 12))
        self.empty_row.grid(row=5) # pack()

        # Create label for the robot/instructions text header widget label
        self.robot_text_label = Label(game_information_frame, text="The robot's status:")
        self.robot_text_label.grid(row=6)
        self.robot_text_label.config(font = ("Arial", 14, 'bold')) # specify font

        # Create the text widget
        self.trobot_text_widget = Label(game_information_frame, height = 2, width = 90) 
        self.trobot_text_widget.config(text="", font = ("Arial", 12))
        self.trobot_text_widget.grid(row=7)
        
        # Import the question_mark image using PhotoImage function
        question_image_file_path = os.path.abspath("cardrobot/Other images/question_mark.svg.png")
        original_question_image = Image.open(question_image_file_path).resize((100,100))
        self.resized_question_image = ImageTk.PhotoImage(original_question_image)

        # Create explanation button and make background color green
        self.settings_button = Button(top_frame, image=self.resized_question_image, command = self.open_settings_popup)#, height = 5, width = 5)
        self.settings_button.config(bg='green')
        self.settings_button.grid(row=0, column=3)

        # Call event loop which makes the window appear
        self.root.mainloop()

    def open_settings_popup(self):
        self.settings_popup = Toplevel(self.root)
        self.settings_popup.geometry('900x400')
        self.settings_popup.title("User guide")

        # Create text widget inside window
        self.text = Text(self.settings_popup, state="normal", wrap="word", width=90)
        self.text.grid(row = 0, column = 0, sticky="nsew", padx=2, pady=2)
    
        # Create scrollbar and connect it with text widget
        self.scrollbar = Scrollbar(self.settings_popup, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky="nsew")
        self.text['yscrollcommand'] = self.scrollbar.set

        # Read text from file and insert it into the text widget
        file_path_user_guide = os.path.abspath("User guide.txt")
        with open(file_path_user_guide, encoding='utf-8') as f:
            user_guide_text = f.read()
        self.text.insert('end', user_guide_text)
        self.text.config(state="disabled", font = ("Arial", 12)) # Make it read-only

        # Make the headers of the text bold
        self.text.tag_configure("bold", font=("Arial", 14, "bold"))
        self.text.tag_add("bold", "1.0", "1.10")
        self.text.tag_add("bold", "6.0", "6.10")

    def update_ui(self):
        top_card = self.state.get_top_card()

        file_path_image_1 = os.path.abspath("cardrobot/Playing cards/back of playing card.png")

        original_playing_card_1_image = Image.open(file_path_image_1).resize((150,220))
        self.resize_playing_card_1_image = ImageTk.PhotoImage(original_playing_card_1_image)
        
        self.draw_stack_label.config(image = self.resize_playing_card_1_image)
        file_path_image_2 = os.path.abspath(f"cardrobot/Playing cards/{top_card}.png")

        original_playing_card_2_image = Image.open(file_path_image_2).resize((150,220))
        self.resize_playing_card_2_image = ImageTk.PhotoImage(original_playing_card_2_image)

        self.discard_stack_label.config(image = self.resize_playing_card_2_image) # The top card on the discard stack  
    
    # Updates text widget which shows whose turn it is
    def update_text_ui_turn(self, string):
        self.text_widget_turn.config(text=string, fg='red')
        # Define a new function to change the color to black
        def change_color_to_black():
            self.text_widget_turn.config(fg='black')
        # Schedule the new function to be called after 300ms 
        self.text_widget_turn.after(300, change_color_to_black)

    # Updates text widget which shows the current action robot is performing / an instruction for the player
    def update_text_ui_extra(self, string):
        self.text_widget_extra.config(text=string, fg='red')
         # Define a new function to change the color to black
        def change_color_to_black():
            self.text_widget_extra.config(fg='black')
        # Schedule the new function to be called after 300ms 
        self.text_widget_extra.after(300, change_color_to_black)

    # Updates text widget which shows the action which the robot is performing or the robot instructs the player to do 
    def update_robot_text_ui(self, string):
        self.trobot_text_widget.config(text=string, fg='red')
         # Define a new function to change the color to black
        def change_color_to_black():
            self.trobot_text_widget.config(fg='black')
        # Schedule the new function to be called after 300ms 
        self.trobot_text_widget.after(300, change_color_to_black)

    def player_turn(self, player: PestenPlayer):
        # Empty the extra game state information text widget, because that information does not hold for the next turn
        self.update_text_ui_extra(" ")
        # Update the player turn text widget with whose turn it currently is
        self.update_text_ui_turn(f"It is {player}'s turn")
        self.update_ui()
        pass

    def player_draws(self, player: PestenPlayer, amount: int):
        self.update_ui()
        pass

    def player_plays(self, player: PestenPlayer, card):
        self.update_ui()
        pass

    def player_won(self, player: PestenPlayer):
        self.update_text_ui_turn(f"{player} has won the game!")
        self.update_text_ui_extra(f"{player} has won the game!")
        pass

    def effect_draw_cards(self, amount: int): 
        player_turn = self.state.get_current_player()
        self.update_text_ui_extra(f"A(nother) Pestkaart is on the discard stack, player {player_turn} needs to draw {amount} card(s) or throw a pestkaart.")
        pass

    def effect_reverse_direction(self, is_clockwise: bool):
        if is_clockwise:
            self.update_text_ui_extra("The play direction is now clockwise.")
        else:
            self.update_text_ui_extra("The play direction is now counterclockwise.")
        pass

    def effect_extra_turn(self, player):
        self.update_text_ui_extra(f"{player} gets an extra turn for playing this card.")
        pass
    
    def effect_skip_turn(self):
        next_player_turn = self.state.next_player()
        self.update_text_ui_extra(f"The turn of player {next_player_turn} is skipped.")
        pass

    def __deepcopy__(self, obj):
        return None

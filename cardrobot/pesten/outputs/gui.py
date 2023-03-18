from game.output import GameOutput
from pesten.types import PestenOutputType
from pesten.player import PestenPlayer
from pesten.state import PestenGameState
from PIL import Image, ImageTk
from tkinter import Frame, LabelFrame
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
        #root.iconbitmap()
        self.root.geometry("900x500")
        self.root.configure(background="green")

        # Create the top frame, containing the cards
        top_frame = Frame(self.root, background = "green")

        # Create the bottom frame, containing the text widget
        bottom_frame = Frame(self.root, background = "purple")

        # Layout of the two frames inside root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) 

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
        self.draw_stack_label = Label(draw_stack_frame, text="")
        self.draw_stack_label.pack(pady=20)

        self.discard_stack_label = Label(discard_stack_frame, text="")
        self.discard_stack_label.pack(pady=20)

        # Create label for the text widget
        self.text_widget_label = Label(user_information_widget, text="The current game status:")
        self.text_widget_label.pack()
        self.text_widget_label.config(font = ("Arial", 12)) # specify font

        # Create the text widgets
        self.text_widget_turn = Label(user_information_widget, height = 2, width = 80, text="") 
        self.text_widget_turn.config(text="")
        self.text_widget_turn.pack()

        self.text_widget_extra = Label(user_information_widget, height = 2, width = 80, text="") 
        self.text_widget_extra.config(text="")
        self.text_widget_extra.pack()

        # Call event loop which makes the window appear
        self.root.mainloop()

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
        self.text_widget_turn.config(text=string)

    # Updates text widget which shows the current action robot is performing / an instruction for the player
    def update_text_ui_extra(self, string):
        self.text_widget_extra.config(text=string)

    def player_turn(self, player: PestenPlayer):
        self.update_text_ui_turn(f"It is player {player}'s turn")
        self.update_ui()
        pass

    def player_draws(self, player: PestenPlayer, amount: int):
        self.update_ui()
        pass

    def player_plays(self, player: PestenPlayer, card):
        self.update_ui()
        pass

    def player_won(self, player: PestenPlayer):
        self.update_text_ui_turn(f"Player {player} has won the game!")
        self.update_text_ui_extra(f"Player {player} has won the game!")
        pass

    def effect_draw_cards(self, amount: int): #TODO: add parameter, which shows which player's turn it is currently
        self.update_text_ui_turn(f"Pestkaart(en) is/are on the discard stack, {amount} cards need to be drawn or a pestkaart needs to be thrown.")
        pass

    def effect_reverse_direction(self, is_clockwise: bool):
        if is_clockwise:
            self.update_text_ui_extra("The play direction is now clockwise.")
        else:
            self.update_text_ui_extra("The play direction is now counterclockwise.")
        pass

    def effect_extra_turn(self):
        self.update_text_ui_extra("The player gets an extra turn for playing this card.")
        pass
    
    def effect_skip_turn(self):
        self.update_text_ui_extra("The turn of the next player is skipped.")
        pass

    def __deepcopy__(self, obj):
        return None

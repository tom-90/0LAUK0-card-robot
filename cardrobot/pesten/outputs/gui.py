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
        
        main_frame = Frame(self.root, background = "green")
        main_frame.pack(pady=20)

        # Create the frames for the two game stacks and the two hands
        draw_stack_frame = LabelFrame(main_frame, text="Draw stack", border=0)
        draw_stack_frame.grid(row=0, column=2, padx=20, pady=40, ipadx=20)

        discard_stack_frame = LabelFrame(main_frame, text="Discard stack", border=0)
        discard_stack_frame.grid(row=0, column=3, padx=20, pady=40, ipadx=20)

        # Put cards in the frames, this is done by putting images into labels
        self.draw_stack_label = Label(draw_stack_frame, text="")
        self.draw_stack_label.pack(pady=20)

        self.discard_stack_label = Label(discard_stack_frame, text="")
        self.discard_stack_label.pack(pady=20)

        # Call event loop which makes the window appear
        self.root.mainloop()

    def update_ui(self):
        top_card = self.state.get_top_card()

        file_path_image_1 = os.path.abspath("cardrobot/Playing cards/back of playing card.png")

        original_playing_card_1_image = Image.open(file_path_image_1).resize((150,220))
        self.resize_playing_card_1_image = ImageTk.PhotoImage(original_playing_card_1_image)
        
        self.draw_stack_label.config(image = self.resize_playing_card_1_image)
        # TODO: add textbar which shows the current action robot is performing / instruction player

        file_path_image_2 = os.path.abspath(f"cardrobot/Playing cards/{top_card}.png")

        original_playing_card_2_image = Image.open(file_path_image_2).resize((150,220))
        self.resize_playing_card_2_image = ImageTk.PhotoImage(original_playing_card_2_image)

        self.discard_stack_label.config(image = self.resize_playing_card_2_image) # The top card on the discard stack  

    def player_turn(self, player: PestenPlayer):
        self.update_ui()
        pass

    def player_draws(self, player: PestenPlayer, amount: int):
        self.update_ui()
        pass

    def player_plays(self, player: PestenPlayer, card):
        self.update_ui()
        pass

    def player_won(self, player: PestenPlayer):
        # TODO: Implement some sort of display for this if we want
        pass

    def effect_draw_cards(self, amount: int):
        # TODO: Implement some sort of display for this if we want
        pass

    def effect_reverse_direction(self, is_clockwise: bool):
        # TODO: Implement some sort of display for this if we want
        pass

    def effect_extra_turn(self):
        # TODO: Implement some sort of display for this if we want
        pass
    
    def effect_skip_turn(self):
        # TODO: Implement some sort of display for this if we want
        pass

    def __deepcopy__(self, obj):
        return None
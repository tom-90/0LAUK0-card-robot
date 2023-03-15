from game.input import GameInput
from game.cards import Card
from pesten.types import PestenInputType
from pesten.state import PestenGameState

suit_map = {
    "D": 1, # Diamonds/ruiten
    "H": 2, # Hearts/harten
    "S": 3, # Spades/schoppen
    "C": 4  # Clubs/klaveren
}

rank_map = {
    "A": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13
}

class TerminalInput(GameInput):
    state: PestenGameState

    def __init__(self, state):
        super().__init__(state)

        self.register(PestenInputType.READ_TOP_CARD, self.get_top_card)
        self.register(PestenInputType.READ_DRAWN_CARD, self.get_drawn_card)
        self.register(PestenInputType.WAIT_FOR_SHUFFLE, self.wait_for_shuffle)
        self.register(PestenInputType.WAIT_FOR_TOP_CARD, self.wait_for_top_card)
        self.register(PestenInputType.WAIT_FOR_PLAY_OR_DRAW, self.wait_for_play_or_draw)

    def get_top_card(self):
        card = None

        while card is None:
            card = self.input_to_card(self.input("What is the card on top of the discard stack? "))

        return card

    def get_drawn_card(self):
        card = None

        while card is None:
            card = self.input_to_card(self.input("Please draw a card and enter the card you drew: "))

        return card

    def wait_for_shuffle(self):
        self.input("Please shuffle the deck and press enter when you are ready to continue.")

    def wait_for_top_card(self, card: Card):
        self.input(f"Please put the {card} on top of the discard stack and press enter when you are ready to continue.")
    
    def wait_for_play_or_draw(self):
        to_draw = 1
        if self.state.pestkaarten_sum > 0:
            to_draw = self.state.pestkaarten_sum
            print(f"You need to throw a 'pestkaart' or you will be forced to draw {self.state.pestkaarten_sum} new cards.")

        card = None
        while card is None:
            response = self.input(f"Play a card and enter it here, or press enter if you want to draw {to_draw} card(s): ")
            if response == "":
                return None

            card = self.input_to_card(response)

        return card

    def input_to_card(self, input: str) -> Card | None:
        input = input.upper()

        if input == "J":
            return Card(0, 0)
        
        for rank in rank_map:
            for suit in suit_map:
                if input == rank + suit:
                    return Card(rank_map[rank], suit_map[suit])

        print(f"'{input}' is not a valid card")
        return None
    
    def input(self, message: str) -> str:
        return input(message)
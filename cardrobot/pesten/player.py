from game.player import Player
from game.cards import CardStack
from pesten.state import PestenGameState

class PestenPlayer(Player):
    hand: CardStack
    state: PestenGameState
    type: str

    def __init__(self, state):
        assert isinstance(state, PestenGameState), "PestenPlayer can only be used with PestenGameState"
        super().__init__(state)

        self.hand = CardStack()

    def __str__(self):
        return f"{self.type.capitalize()} player {self.index}"

    def __repr__(self):
        return f"{self.type}-{self.index}"
from __future__ import annotations
from game.state import GameState
from game.cards import UnknownCard, CardStack, Card
from pesten.types import PestenInputType, PestenOutputType

from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from pesten.player import PestenPlayer

class PestenGameState(GameState):
    discard_stack: CardStack
    draw_stack: CardStack

    pestkaarten_sum: int = 0
    play_direction: int = 1
    difficulty: int = 0.5

    def __init__(self):
        super().__init__()

        self.discard_stack = CardStack()
        self.draw_stack = CardStack()

    def setup(self):
        super().setup()
        self.discard_stack.clear()

        self.draw_stack += [UnknownCard() for _ in range(53)]
        self.discard_stack += self.input(PestenInputType.READ_TOP_CARD)
        while (self.get_top_card().rank_id in [0,2]):
            self.discard_stack += self.input(PestenInputType.READ_TOP_CARD)
            self.draw_stack.pop()

        self.pestkaarten_sum = 0
        self.play_direction = 1
        self.difficulty = 0.5

        for player in self.players:
            player.hand.clear()
            player.draw_cards(7)

    def has_started(self):
        return self.next_player_index >= 0

    def is_finished(self, silent=False):
        for player in self.players:
            if len(player.hand) == 0:
                if not silent:
                    self.output(PestenOutputType.PLAYER_WON, player)
                return True

        return False

    def get_top_card(self):
        assert len(self.discard_stack) > 0, "There is no top card on an empty discard stack"
        return self.discard_stack.cards[-1]

    def next_player(self) -> PestenPlayer:
        assert len(self.players) > 0, "GameState should have at least one player"
        self.next_player_index = (self.next_player_index + self.play_direction) % len(self.players)
        return self.players[self.next_player_index]

    # applies the special effect of the given card if it has any
    # returns whether the turn is over or not
    def apply_card_effect(self, card, virtual = False):
        if (card.rank_id in [0,2]): # If chosen move is playing a "pestkaart"
            self.pestkaarten_sum += (5 if card.rank_id == 0 else 2) # Increase pestkaarten_sum accordingly
            if not virtual:
                self.output(PestenOutputType.EFFECT_DRAW_CARDS, (5 if card.rank_id == 0 else 2))
        elif (card.rank_id == 1): # If chosen move is an ace, the direction of play is reversed
            self.play_direction *= -1
            if not virtual:
                self.output(PestenOutputType.EFFECT_REVERSE_DIRECTION, self.play_direction == 1)
        elif (card.rank_id == 7): # If chosen move is playing a card with rank 7, the turn is not over
            if not virtual:
                self.output(PestenOutputType.EFFECT_EXTRA_TURN)
            return False
        elif (card.rank_id == 8): # If chosen move is playing a card with rank 8, the turn of the next player is skipped
            if not virtual:
                self.output(PestenOutputType.EFFECT_SKIP_TURN)
            self.next_player()
        return True

    def reshuffle(self, virtual = False):
        # wait until all cards from the discard stack except the top card are shuffled and added to the draw stack
        if not virtual:
            self.input(PestenInputType.WAIT_FOR_SHUFFLE)

        top_card = self.state.discard_stack.pop()
        count = len(self.state.discard_stack)

        self.state.discard_stack.clear()
        self.state.discard_stack += top_card

        self.state.draw_stack += [UnknownCard() for _ in range(count)]

    # returns whether the given card can be played in the current gamestate
    def is_valid_card(self, card: Card):
        if (0 < self.pestkaarten_sum):
            return card.rank_id in [0,2]
        else:
            top_card = self.get_top_card()
            return ((card.suit_id in [0, top_card.suit_id]) or (top_card.rank_id in [0, card.rank_id]))
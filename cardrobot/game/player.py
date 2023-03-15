from __future__ import annotations
import copy
from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from game.state import GameState


class Player():
    state: GameState
    index: int | None

    def __init__(self, state: GameState):
        self.state = state
        self.index = None

    def set_index(self, index):
        self.index = index

    def __eq__(self, other: Player):
        return self.index == other.index
    
    def copy(self, state: GameState):
        clone = copy.deepcopy(self)
        if clone is None:
            return None
        clone.state = state
        return clone

    # Methods to be implemented by subclasses
    def do_turn():
        raise NotImplementedError()
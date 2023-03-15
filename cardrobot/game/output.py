from __future__ import annotations
import copy
from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from game.state import GameState
from enum import Enum

class OutputType(str, Enum):
    pass

class GameOutput():
    state: GameState
    handlers: dict[OutputType, callable]

    def __init__(self, state: GameState):
        self.state = state
        self.handlers = {}

    def destroy(self):
        pass

    def copy(self, state: GameState):
        clone = copy.deepcopy(self)
        if clone is None:
            return None
        clone.state = state
        return clone

    def register(self, type: OutputType, handler: callable):
        self.handlers[type] = handler

    def is_handled(self, type: OutputType):
        return type in self.handlers

    def handle(self, type: OutputType, *args, **kwargs):
        return self.handlers[type](*args, **kwargs)

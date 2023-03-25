from __future__ import annotations
import copy
from enum import Enum
from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from game.state import GameState

class InputType(str, Enum):
    pass

class GameInput():
    state: GameState
    handlers: dict[InputType, callable]

    def __init__(self, state: GameState):
        self.state = state
        self.handlers = {}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.state})"

    def destroy(self):
        pass

    def copy(self, state: GameState):
        clone = copy.deepcopy(self)
        if clone is None:
            return None
        clone.state = state
        return clone

    def register(self, type: InputType, handler: callable):
        self.handlers[type] = handler

    def is_handled(self, type: InputType):
        return type in self.handlers

    def handle(self, type: InputType, *args, **kwargs):
        return self.handlers[type](*args, **kwargs)

import copy
from game.player import Player
from game.input import GameInput, InputType
from game.output import GameOutput, OutputType

class GameState():
    players: list[Player]
    next_player_index = -1
    has_started = False
    inputs: list[GameInput]
    outputs: list[GameOutput]

    def __init__(self):
        self.players = []
        self.inputs = []
        self.outputs = []

    def setup(self):
        self.has_started = False
        self.next_player_index = -1

    def destroy(self):
        for input in self.inputs:
            input.destroy()
        for output in self.outputs:
            output.destroy()
        self.inputs = []
        self.outputs = []

    def next_player(self) -> Player:
        assert len(self.players) > 0, "GameState should have at least one player"
        self.next_player_index = (self.next_player_index + 1) % len(self.players)
        return self.players[self.next_player_index]

    def get_current_player(self) -> Player:
        assert len(self.players) > 0, "GameState should have at least one player"
        return self.players[self.next_player_index]

    def set_current_player(self, player):
        if player is None:
            self.next_player_index = -1
        else:
            self.next_player_index = player.index

    def add_player(self, player: Player):
        player.set_index(len(self.players))
        self.players.append(player)

        return self

    def copy(self):
        clone = copy.copy(self)

        clone.players = []
        clone.inputs = []
        clone.outputs = []

        for player in self.players:
            clone.add_player(player.copy(clone))
        for input in self.inputs:
            clone.use(input.copy(clone))
        for output in self.outputs:
            clone.use(output.copy(clone))
        
        return clone

    def do_game(self, difficulty: float = 0.0):
        self.has_started = True
        while not self.is_finished():
            player = self.next_player()
            if player.type == "robot":
                player.do_turn(difficulty)
            else:
                player.do_turn()

        return self.get_winner()

    def use(self, io: GameInput | GameOutput | None):
        if isinstance(io, GameInput):
            self.inputs.append(io)
        elif isinstance(io, GameOutput):
            self.outputs.append(io)
        elif io is None:
            return self
        else:
            raise Exception("Unknown IO type")

        io.state = self

        return self

    def input(self, type: InputType, *args, **kwargs):
        for input in self.inputs:
            if input.is_handled(type):
                return input.handle(type, *args, **kwargs)
        raise Exception("No input handler for type " + type)

    def output(self, type: OutputType, *args, **kwargs):
        for output in self.outputs:
            if output.is_handled(type):
                output.handle(type, *args, **kwargs)

    # Methods to be implemented by subclasses
    def is_finished(self):
        raise NotImplementedError()


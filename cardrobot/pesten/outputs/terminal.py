from game.output import GameOutput
from pesten.types import PestenOutputType
from pesten.player import PestenPlayer

class TerminalOutput(GameOutput):
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
        self.register(PestenOutputType.ROBOT_MOVE_STATS, self.robot_move_stats)

    def player_turn(self, player: PestenPlayer):
        print(f"It is {player}'s turn.")
        print(f" - Player's hand: {player.hand}")
        print(f" - Top card: {player.state.get_top_card()}")

    def player_draws(self, player: PestenPlayer, amount: int):
        print(f"{player} draws {amount} card(s).")

    def player_plays(self, player: PestenPlayer, card):
        if not self.state.is_valid_card(card):
            print(f"{player} played an invalid card: {card}. Continuing anyway.")
        else:
            print(f"{player} plays {card}.")

    def player_won(self, player: PestenPlayer):
        print(f"{player} won the game!")

    def effect_draw_cards(self, amount: int):
        print(f"The next player needs to draw {amount} extra cards.")

    def effect_reverse_direction(self, is_clockwise: bool):
        print(f"The direction of play has been reversed and is now {'clockwise' if is_clockwise else 'counter-clockwise'}.")

    def effect_extra_turn(self):
        print(f"The current player gets an extra turn.")
    
    def effect_skip_turn(self):
        print(f"The next player is forced to skip their turn.")

    def robot_move_stats(self, player: PestenPlayer, valid_moves, move_scores, move_probs):
        # Debugging info
        print(f"{player} found {len(valid_moves)} valid moves:")
        for i, move in enumerate(valid_moves):
            if move == -1:
                move = "Draw"
            print(f" - {move} (score: {move_scores[i]}, prob: {move_probs[i]:.2f})")
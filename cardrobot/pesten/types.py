from game.output import OutputType
from game.input import InputType

class PestenOutputType(OutputType):
    PLAYER_TURN = 'player_turn'
    PLAYER_DRAWS = 'player_draws'
    PLAYER_PLAYS = 'player_plays'
    PLAYER_WON = 'player_won'

    EFFECT_DRAW_CARDS = 'effect_draw_cards'
    EFFECT_REVERSE_DIRECTION = 'effect_reverse_direction'
    EFFECT_EXTRA_TURN = 'effect_extra_turn'
    EFFECT_SKIP_TURN = 'effect_skip_turn'

    ROBOT_MOVE_STATS = 'robot_move_stats' # Debugging

class PestenInputType(InputType):
    READ_TOP_CARD = 'read_top_card'
    READ_DRAWN_CARD = 'read_drawn_card'
    WAIT_FOR_SHUFFLE = 'wait_for_shuffle'
    WAIT_FOR_TOP_CARD = 'wait_for_top_card'
    WAIT_FOR_PLAY_OR_DRAW = 'wait_for_play_or_draw'
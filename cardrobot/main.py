from dotenv import load_dotenv
load_dotenv()

from pesten.state import PestenGameState
from pesten.robot import PestenRobotPlayer
from pesten.human import PestenHumanPlayer
from pesten.inputs.saved_terminal import SavedTerminalInput
from pesten.inputs.terminal import TerminalInput
from pesten.inputs.camera import CameraInput
from pesten.outputs.terminal import TerminalOutput
from pesten.outputs.gui import GUIOutput
from threading import Thread
from pesten.types import PestenInputType, PestenOutputType
import time
import math

# TODO: tune the delta difficulty to converge to the desired win ratio faster
def new_difficulty(old_difficulty: float, real_win_ratio: float, gametime_s: float, static_difficulty: bool = False) -> float:
    difficulty = old_difficulty
    if not static_difficulty:
        # note that the difficulty changes at most 0.3 per game

        # if the player wins more than 70% of the games, the difficulty should be decreased, else increased
        # this atan function is scaled to the range [-0.2, 0.2] and crosses the x-axis at 0.7
        winratio_deltadiff = 0.2 * math.atan(5 * (real_win_ratio - 0.7)) * (2.0 / math.pi) # note to self: increase multiplier inside atan to strengthen the change
        # if the player finished the game in less than 5 minutes, the difficulty should be increased more, else decreased
        # this atan function is scaled to the range [-0.1, 0.1] and crosses the x-axis at 300 sec (5 minutes)
        gametime_deltadiff = 0.1 * math.atan((gametime_s / 60.0) - 5.0) * (-2.0 / math.pi)

        difficulty += winratio_deltadiff + gametime_deltadiff

    return min(1.0, max(0.0, difficulty))

def playsession(state: PestenGameState, robotwins=0, playerwins=0):
    robot_total_wins = robotwins
    player_total_wins = playerwins
    use_mcts = state.input(PestenInputType.USE_MCTS)
    difficulty = state.input(PestenInputType.STARTING_DIFFICULTY)
    
    global playsession_done
    while not playsession_done:
        state.output(PestenOutputType.CURRENT_DIFFICULTY, difficulty)

        state.setup()
        gamestarttime = time.time()
        winner = state.do_game(difficulty, use_mcts)
        if (winner.type == "robot"):
            robot_total_wins += 1
        else:
            player_total_wins += 1

        gametime = time.time() - gamestarttime
        win_ratio = player_total_wins/(player_total_wins+robot_total_wins) if (player_total_wins+robot_total_wins) > 0 else 0
        print(f"gametime: {gametime}, Player wins: {player_total_wins}, Robot wins: {robot_total_wins}, win ratio: {win_ratio}")

        difficulty = new_difficulty(difficulty, win_ratio, gametime, static_difficulty=False)

        playsession_done = not state.input(PestenInputType.PLAY_AGAIN)
    return True

if __name__ == "__main__":
    state = PestenGameState()

    state.add_player(PestenRobotPlayer(state))
    state.add_player(PestenHumanPlayer(state))

    state.use(CameraInput(state))
    state.use(TerminalInput(state))
    state.use(TerminalOutput(state))
    state.use(GUIOutput(state))

    global playsession_done
    playsession_done = False

    game_thread = Thread(target=playsession, args=[state])
    game_thread.daemon = True
    game_thread.start()

    
    try:
        while not playsession_done:
            time.sleep(1)
    except Exception as e:
        print("\nGame interrupted")

    state.destroy()

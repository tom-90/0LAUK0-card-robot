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
from time import sleep
from pesten.types import PestenInputType, PestenOutputType

# TODO: tune the delta difficulty to converge to the desired win ratio faster
def new_difficulty(old_difficulty: float, real_win_ratio: float, desired_win_ratio: float, static_difficulty: bool = False) -> float:
    difficulty = old_difficulty
    if not static_difficulty:
        delta_difficulty = (real_win_ratio - desired_win_ratio) ** 3
        difficulty = old_difficulty + delta_difficulty

    return min(1.0, max(0.0, difficulty))

def playsession(state: PestenGameState):
    robot_total_wins = 0
    player_total_wins = 0
    use_mcts = state.input(PestenInputType.USE_MCTS)
    difficulty = state.input(PestenInputType.STARTING_DIFFICULTY)
    
    global playsession_done
    while not playsession_done:
        state.output(PestenOutputType.CURRENT_DIFFICULTY, difficulty)

        state.setup()

        winner = state.do_game(difficulty, use_mcts)
        if (winner.type == "robot"):
            robot_total_wins += 1
        else:
            player_total_wins += 1

        win_ratio = player_total_wins/(player_total_wins+robot_total_wins) if (player_total_wins+robot_total_wins) > 0 else 0
        print(f"Player wins: {player_total_wins}, Robot wins: {robot_total_wins}, win ratio: {win_ratio}")

        difficulty = new_difficulty(difficulty, win_ratio, 0.7, static_difficulty=False)

        playsession_done = not state.input(PestenInputType.PLAY_AGAIN)
    return True

if __name__ == "__main__":
    state = PestenGameState()

    state.add_player(PestenRobotPlayer(state))
    state.add_player(PestenHumanPlayer(state))

    # input = SavedTerminalInput(state, "saved_inputs.txt") Use this to load saved inputs
    input = SavedTerminalInput(state)

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
            sleep(1)
    except Exception as e:
        print("\nGame interrupted")

    input.save("saved_inputs.txt")

    state.destroy()

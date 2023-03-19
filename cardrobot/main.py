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

def start_game(state: PestenGameState):
    state.setup()
    state.do_game()

if __name__ == "__main__":
    state = PestenGameState()

    state.add_player(PestenRobotPlayer(state))
    state.add_player(PestenHumanPlayer(state))

    # input = SavedTerminalInput(state, "saved_inputs.txt") Use this to load saved inputs
    input = SavedTerminalInput(state)

    state.use(CameraInput(state))
    state.use(TerminalOutput(state))
    state.use(GUIOutput(state))

    game_thread = Thread(target=start_game, args=[state])
    game_thread.daemon = True
    game_thread.start()

    try:
        while not state.has_started or not state.is_finished(True):
            sleep(1)
    except KeyboardInterrupt:
        print("\nGame interrupted")

    input.save("saved_inputs.txt")

    state.destroy()
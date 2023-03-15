from pesten.inputs.terminal import TerminalInput

class SavedTerminalInput(TerminalInput):
    saved_inputs: list[str]
    inputs: list[str]

    def __init__(self, state, filename: str | None = None):
        super().__init__(state)

        self.saved_inputs = []
        self.inputs = []

        if filename:
            with open(filename, "r") as file:
                self.saved_inputs = file.readlines()
                self.saved_inputs.reverse()

    def input(self, message: str) -> str:
        input = None
        if len(self.saved_inputs) > 0:
            input = self.saved_inputs.pop().rstrip('\n')
            print(message + input)
        else:
            input = super().input(message)
        
        self.inputs.append(input + '\n')

        return input
    
    def save(self, filename: str):
        with open(filename, "w") as file:
            file.writelines(self.inputs)

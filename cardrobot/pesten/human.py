from pesten.player import PestenPlayer
from game.cards import Card
from pesten.types import PestenOutputType, PestenInputType

class PestenHumanPlayer(PestenPlayer):
    type = "human"

    def draw_cards(self, amount: int):
        self.state.output(PestenOutputType.PLAYER_DRAWS, self, amount)
        if len(self.state.draw_stack) < amount:
            self.state.reshuffle()

        for _ in range(amount):
            self.hand += self.state.draw_stack.pop() # Will return UnknownCard

    def do_turn(self):
        turn_over = False
        while not turn_over and not self.state.is_finished():
            self.state.output(PestenOutputType.PLAYER_TURN, self)
            card = self.state.input(PestenInputType.WAIT_FOR_PLAY_OR_DRAW)

            if isinstance(card, Card):
                self.state.output(PestenOutputType.PLAYER_PLAYS, self, card)

                self.hand.pop()
                self.state.discard_stack += card
                turn_over = self.state.apply_card_effect(card)
            else:
                draw_count = self.state.pestkaarten_sum if self.state.pestkaarten_sum > 0 else 1
    
                self.draw_cards(draw_count)

                if self.state.pestkaarten_sum == 0:
                    turn_over = True # Drawing a card by choice, ends the turn

                self.state.pestkaarten_sum = 0
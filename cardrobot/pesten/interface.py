from copy import deepcopy
import random
from game.cards import Card, CardStack
from pesten.player import PestenPlayer

class StateInterface(PestenPlayer):

    def __init__(self, state, hand, pestkaarten_sum):
        self.state = state
        self.hand = hand
        self.pestkaarten_sum = pestkaarten_sum
        self.player_hand = CardStack()
        self.player_hand = self.determinization()
        self.draw_stack = CardStack.standard(1)
        for card in list(self.hand):
            if card in self.draw_stack:
                self.draw_stack -= card
        for card in list(self.state.discard_stack):
            if card in self.draw_stack:
                self.draw_stack -= card
        for card in list(self.player_hand):
            if card in self.draw_stack:
                self.draw_stack -= card
        self.currentPlayer = 1
    
    def determinization(self):
        for player in self.state.players:
            if player.index == 1:
                player_hand_est = CardStack()
                sample_space = CardStack.standard(1)
                for card in list(self.hand):
                    if card in sample_space:
                        sample_space -= card
                for card in list(self.state.discard_stack):
                    if card in sample_space:
                        sample_space -= card
                for i in range(len(player.hand)):
                    card = random.choice(list(sample_space))
                    sample_space -= card
                    player_hand_est += card
                return player_hand_est
        return False
    
    def getCurrentPlayer(self):
        return self.currentPlayer
    
    def getPossibleActions(self):
        valid_moves = []
        if self.currentPlayer == 1:
            for card in self.hand:
                if self.state.is_valid_card(card):
                    valid_moves.append(Action(self.currentPlayer, card.rank_id, card.suit_id))
            valid_moves.append(-1) # -1 stands for voluntarily drawing a card
        elif self.currentPlayer == -1:
            for card in self.player_hand:
                if self.state.is_valid_card(card):
                    valid_moves.append(Action(self.currentPlayer, card.rank_id, card.suit_id))
            valid_moves.append(-1) # -1 stands for voluntarily drawing a card
        return valid_moves
    
    def takeAction(self, action):
        if action != -1:
            card = Card(action.rank_id, action.suit_id)
        else:
            card = -1
        newState = deepcopy(self)
        if (card == -1): # If the player chooses to draw a card
            if (0 < newState.state.pestkaarten_sum): # If the player must draw cards
                newState.draw_cards_mcts(newState.state.pestkaarten_sum, True) # The player draws the mandatory number of cards 
                newState.state.pestkaarten_sum = 0
                newState.currentPlayer = newState.currentPlayer # The player must still play after drawing the forced cards
                return newState
            else:
                newState.draw_cards_mcts(1, True)
                newState.currentPlayer = newState.currentPlayer*-1  # Drawing a card by choice, ends the turn
                return newState
        else:
            if newState.currentPlayer == 1:
                newState.hand -= card
                newState.state.discard_stack += card
            elif newState.currentPlayer == -1:
                newState.player_hand -= card
                newState.state.discard_stack += card

            if (card.rank_id in [0,2]): # If chosen move is playing a "pestkaart"
                newState.pestkaarten_sum += (5 if card.rank_id == 0 else 2) # Increase pestkaarten_sum accordingly
                newState.currentPlayer = newState.currentPlayer*-1
            elif (card.rank_id == 1): # If chosen move is an ace, the direction of play is reversed
                newState.currentPlayer = newState.currentPlayer*-1
            elif (card.rank_id == 7): # If chosen move is playing a card with rank 7, the turn is not over
                newState.currentPlayer = newState.currentPlayer
            elif (card.rank_id == 8): # If chosen move is playing a card with rank 8, the turn of the next player is skipped
                newState.currentPlayer = newState.currentPlayer
            else:
                newState.currentPlayer = newState.currentPlayer*-1

        return newState
    
    def isTerminal(self):
        for player in self.state.players:
            if len(player.hand) == 0:
                return True
        return False

    def getReward(self):
        for player in self.state.players:
            if (len(player.hand) == 0) and (player.index == 0):
                return 100
            elif (len(player.hand) == 0) and (player.index >= 1):
                return -100
        return 0
    
    def draw_cards_mcts(self, amount: int = 1, virtual = False):
        assert 1 <= amount, "amount must be at least 1"
        
        if len(self.draw_stack) < amount:
            top_card = self.state.discard_stack.pop()
    	    
            self.state.discard_stack.clear()
            self.state.discard_stack += top_card

            self.draw_stack = CardStack.standard(1)
            for card in list(self.hand):
                if card in self.draw_stack:
                    self.draw_stack -= card
            for card in list(self.state.discard_stack):
                if card in self.draw_stack:
                    self.draw_stack -= card
            for card in list(self.player_hand):
                if card in self.draw_stack:
                    self.draw_stack -= card

        for _ in range(amount):
            card = self.draw_stack.pop() # Will return UnknownCard

        if self.currentPlayer == 1:
            self.hand += card
        elif self.currentPlayer == -1:
            self.player_hand += card

class Action():
    def __init__(self, player, rank_id, suit_id):
        self.player = player
        self.rank_id = rank_id
        self.suit_id = suit_id
        
    def __str__(self):
        return str((self.rank_id, self.suit_id))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.rank_id == other.rank_id and self.suit_id == other.suit_id and self.player == other.player

    def __hash__(self):
        return hash((self.player, self.rank_id, self.suit_id))

from __future__ import annotations

class Card():
    def __init__ (self, rank_id, suit_id):
        self.suit_id = suit_id
        self.rank_id = rank_id

    def rank_name(self):
        if self.rank_id == 0:
            return "*Joker"
        elif self.rank_id == 1:
            return "Ace"
        elif self.rank_id == 11:
            return "Jack"
        elif self.rank_id == 12:
            return "Queen"
        elif self.rank_id == 13:
            return "King"
        elif 2 <= self.rank_id <= 10: # cards with 2 <= number <= 10
            return str(self.rank_id)
        else:
            raise ValueError("Rank id " + str(self.rank_id) + " is not a valid rank")

    def suit_name(self):
        if self.suit_id == 0:
            return "*Joker"
        elif self.suit_id == 1:
            return "Diamonds" # "Ruiten"
        elif self.suit_id == 2:
            return "Hearts" # "harten"
        elif self.suit_id == 3: 
            return "Spades" # "Schoppen"
        elif self.suit_id == 4:
            return "Clubs" # "Klaveren"
        else:
            raise ValueError("Suit id " + str(self.suit_id) + " is not a valid suit")

    def short_name(self):
        if 2 <= self.rank_id <= 10:
            return self.rank_name() + self.suit_name()[0]
        else:
            return self.rank_name()[0] + self.suit_name()[0]
        
    def long_name(self):
        if self.suit_id == 0:
            return self.rank_name()[1:]
        else:
            return self.rank_name() + " of " + self.suit_name()

    def __str__(self):
        return self.long_name()
    
    def __repr__(self):
        return self.short_name()
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank_id == other.rank_id and self.suit_id == other.suit_id
    
    def __ne__(self, other):
        return not self.__eq__(other)

class UnknownCard(Card):
    def __init__(self):
        self.suit_id = -1
        self.rank_id = -1

    def rank_name(self):
        return "Unknown"

    def suit_name(self):
        return "Unknown"

    def short_name(self):
        return "??"

    def long_name(self):
        return "Unknown Card"

class CardStack():
    cards: list[Card] = []

    def __init__(self, stack: list[Card] | CardStack = []):
        if isinstance(stack, CardStack):
            self.cards = stack.cards.copy()
        else:
            self.cards = stack.copy()

    def push(self, other: Card | list[Card] | CardStack):
        if isinstance(other, Card):
            self.cards = self.cards + [other]
        elif isinstance(other, list):
            self.cards = self.cards + other
        elif isinstance(other, CardStack):
            self.cards = self.cards + other.cards
        else:
            raise TypeError("Cannot add CardStack to object of type " + str(type(other)))

        return self

    def pop(self):
        return self.cards.pop()

    def clear(self):
        return self.cards.clear()

    def __add__(self, other: Card | list[Card] | CardStack):
        return self.push(other)

    def __sub__(self, other: Card | list[Card] | CardStack):
        if isinstance(other, Card):
            self.cards.remove(other)
        elif isinstance(other, list):
            for card in other:
                self.cards.remove(card)
        elif isinstance(other, CardStack):
            for card in other.cards:
                self.cards.remove(card)
        else:
            raise TypeError("Cannot subtract CardStack from object of type " + str(type(other)))

        return self
    
    def __len__(self):
        return len(self.cards)
    
    def __iter__(self):
        return iter(self.cards)
    
    def __str__(self):
        return str(self.cards)
    
    def __repr__(self):
        return repr(self.cards)

    @staticmethod
    def standard(jokers: int = 2):
        deck = CardStack()
        # We add each card to the playing stack once 4 * 13 = 52 cards
        for suit_id in range(1, 4+1):
            for rank_id in range(1, 13+1):
                deck += Card(rank_id, suit_id)

        # Add jokers to the deck
        for _ in range (0, jokers):
            deck += Card(0, 0)
        
        return deck

class UnknownCardStack(CardStack):
    def __init__(self):
        super().__init__()

    def __len__(self):
        raise ValueError("Cannot determine length of unknown card stack")
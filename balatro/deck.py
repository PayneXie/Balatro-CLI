import random
from typing import List, Optional
from .card import Card, Suit, Rank

from enum import Enum, auto

class DeckType(Enum):
    RED = auto()
    BLUE = auto()
    YELLOW = auto()
    CHECKERED = auto()

class Deck:
    def __init__(self, type: DeckType = DeckType.RED):
        self.type = type
        self.cards: List[Card] = []
        self._initialize_deck()

    def _initialize_deck(self):
        self.cards = []
        if self.type == DeckType.CHECKERED:
            # 26 Spades + 26 Hearts
            # 13 Spades (Original)
            for rank in Rank: self.cards.append(Card(Suit.SPADES, rank))
            # 13 Hearts (Original)
            for rank in Rank: self.cards.append(Card(Suit.HEARTS, rank))
            # 13 Spades (Replacing Clubs)
            for rank in Rank: self.cards.append(Card(Suit.SPADES, rank))
            # 13 Hearts (Replacing Diamonds)
            for rank in Rank: self.cards.append(Card(Suit.HEARTS, rank))
        else:
            # Standard 52 cards
            for suit in Suit:
                for rank in Rank:
                    self.cards.append(Card(suit, rank))

    
    def shuffle(self):
        """
        Shuffles the deck using the Fisher-Yates algorithm.
        """
        # Fisher-Yates shuffle
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def draw(self) -> Optional[Card]:
        """
        Draws a card from the top of the deck.
        Returns None if the deck is empty.
        """
        if not self.cards:
            return None
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Deck({len(self.cards)} cards)"

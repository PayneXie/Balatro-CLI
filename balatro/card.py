from enum import IntEnum

class Suit(IntEnum):
    DIAMONDS = 0
    CLUBS = 1
    HEARTS = 2
    SPADES = 3

class Rank(IntEnum):
    TWO = 0
    THREE = 1
    FOUR = 2
    FIVE = 3
    SIX = 4
    SEVEN = 5
    EIGHT = 6
    NINE = 7
    TEN = 8
    JACK = 9
    QUEEN = 10
    KING = 11
    ACE = 12

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def get_value(self) -> int:
        """
        Returns the base chip value of the card.
        2-10: Face value
        J, Q, K: 10
        A: 11
        """
        if self.rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        elif self.rank == Rank.ACE:
            return 11
        else:
            # Rank 0 is TWO, so value is rank + 2
            return self.rank + 2

    def __repr__(self):
        return f"Card(suit={self.suit.name}, rank={self.rank.name})"

    def __str__(self):
        return f"{self.rank.name} of {self.suit.name}"

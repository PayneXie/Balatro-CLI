from enum import IntEnum, auto
from typing import Optional

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

class CardType(IntEnum):
    BASE = 0
    STONE = 1
    GOLD = 2
    STEEL = 3
    GLASS = 4
    LUCKY = 5
    MULT = 6
    BONUS = 7
    WILD = 8

class CardEdition(IntEnum):
    BASE = 0
    FOIL = 1      # +50 Chips
    HOLOGRAPHIC = 2 # +10 Mult
    POLYCHROME = 3  # x1.5 Mult
    NEGATIVE = 4  # +1 Joker Slot

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.enhancement: Optional[CardType] = None
        self.edition: CardEdition = CardEdition.BASE
        
    def get_value(self) -> int:
        """
        Returns the base chip value of the card.
        2-10: Face value
        J, Q, K: 10
        A: 11
        Includes Stone Card check (always 50)
        """
        if self.enhancement == CardType.STONE:
            return 50
            
        if self.rank in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        elif self.rank == Rank.ACE:
            return 11
        else:
            # Rank 0 is TWO, so value is rank + 2
            return self.rank + 2

    def get_chip_bonus(self) -> int:
        """额外筹码加成 (Bonus Card / Foil)"""
        bonus = 0
        if self.enhancement == CardType.BONUS:
            bonus += 30
        if self.edition == CardEdition.FOIL:
            bonus += 50
        return bonus

    def get_mult_bonus(self) -> int:
        """额外倍率加成 (Mult Card / Holographic)"""
        bonus = 0
        if self.enhancement == CardType.MULT:
            bonus += 4
        if self.edition == CardEdition.HOLOGRAPHIC:
            bonus += 10
        return bonus

    def get_xmult_bonus(self) -> float:
        """额外乘倍率加成 (Glass / Polychrome)"""
        # 注意：这里返回的是单个卡牌的乘数，通常是累乘
        # 但在 Balatro 逻辑中，每张卡触发时都会应用乘法
        # 比如两张 Glass 是 x2 x2 = x4
        # 返回 0 表示没有乘数，1 表示 x1 (无变化)
        # 为了方便计算，我们返回实际乘数
        xmult = 1.0
        if self.enhancement == CardType.GLASS:
            xmult *= 2.0
        if self.edition == CardEdition.POLYCHROME:
            xmult *= 1.5
        return xmult

    def __repr__(self):
        extras = []
        if self.enhancement:
            extras.append(self.enhancement.name)
        if self.edition != CardEdition.BASE:
            extras.append(self.edition.name)
        
        base_str = f"Card({self.suit.name}, {self.rank.name})"
        if extras:
            return f"{base_str} [{' '.join(extras)}]"
        return base_str

    def __str__(self):
        s = f"{self.rank.name} of {self.suit.name}"
        if self.enhancement:
            s += f" ({self.enhancement.name})"
        if self.edition != CardEdition.BASE:
            s += f" [{self.edition.name}]"
        return s

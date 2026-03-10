from enum import Enum, auto
from collections import Counter
from typing import List, Tuple, Dict
from .card import Card, Rank, Suit

class HandType(Enum):
    HIGH_CARD = auto()
    PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    STRAIGHT = auto()
    FLUSH = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()

class HandEvaluator:
    # 基础筹码和倍率表
    HAND_SCORES: Dict[HandType, Tuple[int, int]] = {
        HandType.HIGH_CARD: (5, 1),
        HandType.PAIR: (10, 2),
        HandType.TWO_PAIR: (20, 2),
        HandType.THREE_OF_A_KIND: (30, 3),
        HandType.STRAIGHT: (30, 4),
        HandType.FLUSH: (35, 4),
        HandType.FULL_HOUSE: (40, 4),
        HandType.FOUR_OF_A_KIND: (60, 7),
        HandType.STRAIGHT_FLUSH: (100, 8),
        HandType.ROYAL_FLUSH: (100, 8)
    }

    @staticmethod
    def evaluate(cards: List[Card]) -> HandType:
        """
        评估给定的手牌并返回最佳牌型 (HandType)。
        通常处理5张牌，但如果有更多牌，该逻辑主要基于整体统计。
        """
        if not cards:
            return HandType.HIGH_CARD
            
        # 基础统计
        ranks = [c.rank for c in cards]
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)
        
        # 对点数进行排序，用于顺子检查
        # 注意：点数值从 0 (TWO) 到 12 (ACE)
        sorted_unique_ranks = sorted(list(set(ranks)))
        
        is_flush = any(count >= 5 for count in suit_counts.values())
        is_straight = HandEvaluator._check_straight(sorted_unique_ranks)
        
        # 检查同花顺 (Straight Flush) 和 皇家同花顺 (Royal Flush)
        if is_flush and is_straight:
            # 检查是否为皇家同花顺 (Ace, King, Queen, Jack, Ten)
            # Ranks: ACE=12, KING=11, QUEEN=10, JACK=9, TEN=8
            has_ace = Rank.ACE in ranks
            has_king = Rank.KING in ranks
            if has_ace and has_king: 
                 # 如果有 A 和 K 且是顺子，那一定是皇家同花顺或 A 高顺
                 # 但我们已经知道它是同花顺了。
                 # 精确检查：皇家同花顺是 10, J, Q, K, A
                 royal_ranks = {Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE}
                 if royal_ranks.issubset(set(ranks)):
                     return HandType.ROYAL_FLUSH
            return HandType.STRAIGHT_FLUSH
            
        # 检查四条 (Four of a Kind)
        if 4 in rank_counts.values():
            return HandType.FOUR_OF_A_KIND
            
        # 检查葫芦 (Full House, 3 + 2)
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            return HandType.FULL_HOUSE
            
        # 检查同花 (Flush)
        if is_flush:
            return HandType.FLUSH
            
        # 检查顺子 (Straight)
        if is_straight:
            return HandType.STRAIGHT
            
        # 检查三条 (Three of a Kind)
        if 3 in rank_counts.values():
            return HandType.THREE_OF_A_KIND
            
        # 检查两对 (Two Pair)
        # 统计有多少个点数出现了恰好 2 次
        pair_count = list(rank_counts.values()).count(2)
        if pair_count >= 2:
            return HandType.TWO_PAIR
            
        # 检查对子 (Pair)
        if 2 in rank_counts.values():
            return HandType.PAIR
            
        return HandType.HIGH_CARD

    @staticmethod
    def _check_straight(sorted_unique_ranks: List[Rank]) -> bool:
        """
        检查提供的已排序唯一及点数列表是否包含至少5张牌的顺子。
        """
        if len(sorted_unique_ranks) < 5:
            return False
            
        # 将点数转换为整数值以便比较
        # Rank 枚举值本身就是整数
        rank_values = [r.value for r in sorted_unique_ranks]
        
        # 检查常规顺子
        for i in range(len(rank_values) - 4):
            if rank_values[i+4] == rank_values[i] + 4:
                return True
                
        # 检查 A 低顺子 (A, 2, 3, 4, 5)
        # 在我们的枚举中: A=12, 2=0, 3=1, 4=2, 5=3
        # 如果我们有 A, 2, 3, 4, 5, 排序后的唯一值是 [0, 1, 2, 3, 12]
        if Rank.ACE in sorted_unique_ranks:
            low_straight_ranks = {Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.ACE}
            if low_straight_ranks.issubset(set(sorted_unique_ranks)):
                return True
                
        return False

    @staticmethod
    def calculate_score(cards: List[Card]) -> Tuple[int, int, int]:
        """
        计算给定手牌的得分。
        返回: (总分, 基础筹码, 倍率)
        注意：这里只实现了基础计分，没有Joker加成。
        """
        hand_type = HandEvaluator.evaluate(cards)
        base_chips, mult = HandEvaluator.HAND_SCORES[hand_type]
        
        # 计算卡牌筹码
        card_chips = sum(card.get_value() for card in cards)
        
        # 总筹码 = 基础筹码 + 卡牌筹码
        total_chips = base_chips + card_chips
        
        # 总分 = 总筹码 * 倍率
        score = total_chips * mult
        
        return score, total_chips, mult

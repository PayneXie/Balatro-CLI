import unittest
from balatro.deck import Deck
from balatro.card import Card

class TestHandDeal(unittest.TestCase):
    def test_deal_hand(self):
        """
        模拟发牌过程：
        1. 初始化一副新牌
        2. 洗牌
        3. 发出初始手牌（例如8张）
        4. 验证手牌数量和剩余牌堆数量
        """
        # 1. 初始化
        deck = Deck()
        initial_deck_size = len(deck)
        self.assertEqual(initial_deck_size, 52, "初始牌堆应有52张牌")
        
        # 2. 洗牌
        deck.shuffle()
        
        # 3. 发初始手牌 (模拟游戏开始发8张牌)
        hand_size = 8
        hand: list[Card] = []
        
        print(f"\n--- 开始发牌 (目标: {hand_size}张) ---")
        for i in range(hand_size):
            card = deck.draw()
            self.assertIsNotNone(card, "牌堆不应为空")
            hand.append(card)
            print(f"发牌第 {i+1} 张: {card} (值: {card.get_value()})")
            
        print(f"--- 发牌结束 ---\n")
        
        # 4. 验证
        self.assertEqual(len(hand), hand_size, f"手牌数量应为 {hand_size}")
        self.assertEqual(len(deck), initial_deck_size - hand_size, f"牌堆剩余数量应为 {initial_deck_size - hand_size}")
        
        # 打印当前手牌详情
        print(f"当前手牌 ({len(hand)}张):")
        print(", ".join([str(c) for c in hand]))
        print(f"牌堆剩余: {len(deck)}张")

if __name__ == '__main__':
    unittest.main()

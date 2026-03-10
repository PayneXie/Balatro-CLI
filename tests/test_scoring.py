import unittest
from balatro.card import Card, Suit, Rank
from balatro.hand_analysis import HandEvaluator, HandType

class TestScoring(unittest.TestCase):
    def test_high_card_score(self):
        # High Card (5 Chips, 1 Mult)
        # Cards: A(11) + 9(9) + 7(7) + 5(5) + 2(2) = 34 Card Chips
        # Total Chips = 5 (Base) + 34 = 39
        # Score = 39 * 1 = 39
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.HIGH_CARD)
        score, chips, mult = HandEvaluator.calculate_score(cards)
        self.assertEqual(chips, 39)
        self.assertEqual(mult, 1)
        self.assertEqual(score, 39)

    def test_pair_score(self):
        # Pair (10 Chips, 2 Mult)
        # Cards: 8(8) + 8(8) + K(10) + 5(5) + 2(2) = 33 Card Chips
        # Total Chips = 10 (Base) + 33 = 43
        # Score = 43 * 2 = 86
        cards = [
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.KING),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.PAIR)
        score, chips, mult = HandEvaluator.calculate_score(cards)
        self.assertEqual(chips, 43)
        self.assertEqual(mult, 2)
        self.assertEqual(score, 86)

    def test_straight_flush_score(self):
        # Straight Flush (100 Chips, 8 Mult)
        # Cards: 9(9) + 8(8) + 7(7) + 6(6) + 5(5) = 35 Card Chips
        # Total Chips = 100 (Base) + 35 = 135
        # Score = 135 * 8 = 1080
        cards = [
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.HEARTS, Rank.FIVE)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.STRAIGHT_FLUSH)
        score, chips, mult = HandEvaluator.calculate_score(cards)
        self.assertEqual(chips, 135)
        self.assertEqual(mult, 8)
        self.assertEqual(score, 1080)

if __name__ == '__main__':
    unittest.main()

import unittest
from balatro.card import Card, Suit, Rank
from balatro.hand_analysis import HandEvaluator, HandType

class TestHandEvaluator(unittest.TestCase):
    def test_high_card(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.HIGH_CARD)

    def test_pair(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.PAIR)

    def test_two_pair(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.TWO_PAIR)

    def test_three_of_a_kind(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.THREE_OF_A_KIND)

    def test_straight(self):
        # Regular straight 5-9
        cards = [
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.SPADES, Rank.SIX),
            Card(Suit.HEARTS, Rank.FIVE)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.STRAIGHT)

        # Ace-low straight A-5
        cards = [
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FOUR),
            Card(Suit.DIAMONDS, Rank.THREE),
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.HEARTS, Rank.ACE)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.STRAIGHT)
        
        # Ace-high straight 10-A
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.QUEEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.HEARTS, Rank.TEN)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.STRAIGHT)

    def test_flush(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.FLUSH)

    def test_full_house(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.SPADES, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SEVEN)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.FULL_HOUSE)

    def test_four_of_a_kind(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.HEARTS, Rank.TWO)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.FOUR_OF_A_KIND)

    def test_straight_flush(self):
        cards = [
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.HEARTS, Rank.FIVE)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.STRAIGHT_FLUSH)

    def test_royal_flush(self):
        cards = [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.HEARTS, Rank.TEN)
        ]
        self.assertEqual(HandEvaluator.evaluate(cards), HandType.ROYAL_FLUSH)

if __name__ == '__main__':
    unittest.main()

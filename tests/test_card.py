import unittest
from balatro.card import Card, Suit, Rank

class TestCard(unittest.TestCase):
    def test_card_creation(self):
        card = Card(Suit.HEARTS, Rank.ACE)
        self.assertEqual(card.suit, Suit.HEARTS)
        self.assertEqual(card.rank, Rank.ACE)

    def test_card_values(self):
        # Test number cards
        two = Card(Suit.DIAMONDS, Rank.TWO)
        self.assertEqual(two.get_value(), 2)

        seven = Card(Suit.CLUBS, Rank.SEVEN)
        self.assertEqual(seven.get_value(), 7)

        ten = Card(Suit.SPADES, Rank.TEN)
        self.assertEqual(ten.get_value(), 10)

        # Test face cards
        jack = Card(Suit.HEARTS, Rank.JACK)
        self.assertEqual(jack.get_value(), 10)

        queen = Card(Suit.HEARTS, Rank.QUEEN)
        self.assertEqual(queen.get_value(), 10)

        king = Card(Suit.HEARTS, Rank.KING)
        self.assertEqual(king.get_value(), 10)

        # Test Ace
        ace = Card(Suit.SPADES, Rank.ACE)
        self.assertEqual(ace.get_value(), 11)

    def test_enums(self):
        self.assertEqual(Suit.DIAMONDS, 0)
        self.assertEqual(Rank.TWO, 0)
        self.assertEqual(Rank.ACE, 12)

if __name__ == '__main__':
    unittest.main()

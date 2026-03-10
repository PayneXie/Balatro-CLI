import unittest
from balatro.deck import Deck
from balatro.card import Card, Suit, Rank

class TestDeck(unittest.TestCase):
    def test_deck_initialization(self):
        deck = Deck()
        self.assertEqual(len(deck), 52)
        
        # Verify all cards are unique
        unique_cards = set()
        for card in deck.cards:
            unique_cards.add((card.suit, card.rank))
        self.assertEqual(len(unique_cards), 52)

    def test_shuffle(self):
        deck = Deck()
        original_order = deck.cards[:]
        
        deck.shuffle()
        shuffled_order = deck.cards
        
        # It's statistically extremely unlikely that a shuffled deck matches the original order
        self.assertNotEqual(original_order, shuffled_order)
        self.assertEqual(len(deck), 52)
        
        # Verify the set of cards is still the same
        original_set = set((c.suit, c.rank) for c in original_order)
        shuffled_set = set((c.suit, c.rank) for c in shuffled_order)
        self.assertEqual(original_set, shuffled_set)

    def test_draw(self):
        deck = Deck()
        initial_len = len(deck)
        
        card = deck.draw()
        self.assertIsInstance(card, Card)
        self.assertEqual(len(deck), initial_len - 1)
        
        # Draw all remaining cards
        for _ in range(initial_len - 1):
            deck.draw()
            
        self.assertEqual(len(deck), 0)
        self.assertIsNone(deck.draw())

if __name__ == '__main__':
    unittest.main()

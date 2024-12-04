# Define the DeckOfCards class in this file
import random


class DeckOfCards:
    def __init__(self, deckSize):
        self.deck = list(range(deckSize))  # Creates a list from 0 to N

    @classmethod
    def from_list(deck_of_cards, list):
        deck = deck_of_cards(len(list))
        deck.deck = list
        return deck

    def print_len(self):
        print(f"this deck has {len(self.deck)} cards left.")

    def print_deck(self):
        print(self.deck)

    def append(self, value):
        self.deck.append(value)
        
    def random_card_index(self):
        return random.randint(0, len(self.deck) - 1)

    def peek_card(self, index):
        return self.deck[index]

    def pull_card(self, index):
        pulled_card = self.peek_card(index)
        last_card = self.deck.pop()
        if index < len(self.deck):
            self.deck[index] = last_card
        return pulled_card, index, last_card

    def pull_random_card(self):
        index = self.random_card_index();
        return self.pull_card(index)
        

def main():
    # Code to execute
    print("Running DeckOfCards main function...")
    deck = DeckOfCards(9)
    deck.print_len()
    
    card = deck.pull_random_card()
    print(f"Pulled a {card}")
    deck.print_len()
    deck.print_deck()
    
    deck = DeckOfCards.from_list([(x, y) for x in range(5) for y in range(5)])
    deck.print_len()
    deck.print_deck()
    card = deck.pull_random_card()
    print(f"Pulled a {card}")
    deck.print_len()
    deck.print_deck()

if __name__ == "__main__":
    main()
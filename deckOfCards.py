# Define the DeckOfCards class in this file
import random


class DeckOfCards:
    def __init__(self, deckSize):
        self.deck = list(range(deckSize))  # Creates a list from 0 to N

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

if __name__ == "__main__":
    main()
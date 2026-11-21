"""
Hangman Word Guessing Game (Console)
------------------------------------
- Picks a random secret word (from words.txt if present, else a built-in list)
- Player guesses one letter at a time, 6 incorrect guesses allowed
- ASCII gallows art updates with each wrong guess
- Repeated guesses are detected and do NOT cost an attempt
"""

import os
import random

MAX_MISTAKES = 6

# Index = number of mistakes made (0..6)
GALLOWS = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """,
]

FALLBACK_WORDS = [
    "python", "variable", "function", "circuit", "resistor", "capacitor",
    "transistor", "sensor", "arduino", "raspberry", "embedded", "voltage",
    "current", "antenna", "firmware", "semiconductor", "microcontroller",
    "algorithm", "internet", "keyboard", "hangman", "engineer", "diode",
]


def load_words(filename="words.txt"):
    """Load words from a text file (one per line); fall back to a built-in list."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip().isalpha() and len(w.strip()) >= 4]
        if words:
            return words
    return FALLBACK_WORDS


def masked_word(secret, guessed):
    """Return the word with unguessed letters hidden, e.g. '_ A _ H E O N'."""
    return " ".join(ch.upper() if ch in guessed else "_" for ch in secret)


def get_guess(guessed):
    """Prompt until the player enters a valid, new single letter."""
    while True:
        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("  Please enter a single letter (a-z).")
        elif guess in guessed:
            print(f"  You already guessed '{guess.upper()}'. Try a different letter.")
        else:
            return guess


def show_status(secret, guessed, mistakes):
    print(GALLOWS[mistakes])
    print("Word:", masked_word(secret, guessed))
    wrong = sorted(g for g in guessed if g not in secret)
    print("Wrong guesses:", " ".join(l.upper() for l in wrong) or "-")
    print(f"Attempts left: {MAX_MISTAKES - mistakes}\n")


def victory_screen(secret):
    print("=" * 40)
    print("   🎉  YOU WON!  🎉")
    print(f"   The word was: {secret.upper()}")
    print("=" * 40)


def defeat_screen(secret):
    print(GALLOWS[MAX_MISTAKES])
    print("=" * 40)
    print("   💀  GAME OVER  💀")
    print(f"   The word was: {secret.upper()}")
    print("=" * 40)


def play_round(words):
    secret = random.choice(words)
    guessed = set()
    mistakes = 0

    print("\n=== HANGMAN ===")
    print(f"I'm thinking of a {len(secret)}-letter word.")

    while mistakes < MAX_MISTAKES:
        show_status(secret, guessed, mistakes)

        if all(ch in guessed for ch in secret):
            break

        guess = get_guess(guessed)
        guessed.add(guess)

        if guess in secret:
            print(f"  Good guess! '{guess.upper()}' is in the word.")
        else:
            mistakes += 1
            print(f"  Sorry, '{guess.upper()}' is not in the word.")

    if all(ch in guessed for ch in secret):
        victory_screen(secret)
    else:
        defeat_screen(secret)


def main():
    words = load_words()
    while True:
        play_round(words)
        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
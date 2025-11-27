import random
import sys
from typing import Set

from AlphabetAwareAutomaton import AlphabetAwareLevelAutomaton
from GeneralAutomaton import GeneralAutomaton
from LevelAutomaton import LevelAutomaton


def read_text_file(path: str) -> str:
    """Read entire file as a single string."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            return text
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)


def generate_valid_subsequence(s: str, length: int = 5) -> str:
    """
    Generate a random *valid subsequence* from s.
    Always valid, because we choose characters in order.
    """
    if not s:
        return ""

    indices = sorted(random.sample(range(len(s)), min(length, len(s))))
    return "".join(s[i] for i in indices)


def generate_invalid_subsequence(s: str, alphabet: Set[str], length: int = 5) -> str:
    """
    Generate a guaranteed *invalid* subsequence:
    Choose characters NOT present in s whenever possible.
    If alphabet fully matches s, generate a character sequence impossible in order.
    """
    missing_chars = list(set("abcdefghijklmnopqrstuvwxyz") - alphabet)

    if missing_chars:
        # Use characters not in the string → always invalid
        return "".join(random.choice(missing_chars) for _ in range(length))

    # If all letters appear, generate an ordered impossibility:
    # e.g., pick a character but repeat it too many times
    c = random.choice(list(alphabet))
    return c * (s.count(c) + 3)  # more occurrences than exist → invalid


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input.txt>")
        sys.exit(1)

    filename = sys.argv[1]
    string = read_text_file(filename)

    if not string:
        print("ERROR: Input text is empty.")
        sys.exit(1)

    alphabet = set(string)

    # Generate test strings
    valid_subseq = generate_valid_subsequence(string, len(string) // 3)
    invalid_subseq = generate_invalid_subsequence(string, alphabet)

    print("Original string length:", len(string))
    print("Alphabet size:", len(alphabet))
    print("Valid subsequence   :", valid_subseq)
    print("Invalid subsequence :", invalid_subseq)
    print("===================================================")

    # Create automata
    genAut = GeneralAutomaton(alphabet, string)
    levAut = LevelAutomaton(alphabet, string, 2)
    awareAut = AlphabetAwareLevelAutomaton(alphabet, string)

    for name, aut in [
        ("General Automaton (SA)", genAut),
        ("Level Automaton (k=2)", levAut),
        ("Alphabet-Aware Level Automaton", awareAut),
    ]:
        print(name)
        print(aut.GetInfo())
        print("Valid subsequence accepted?   ", aut.Compute(valid_subseq))
        print("Invalid subsequence accepted? ", aut.Compute(invalid_subseq))
        print("===================================================")


if __name__ == "__main__":
    main()

"""
Main runner for testing subsequence automata on text loaded from a file.

Given a text file as argument:
    - Read the full contents as the base string S
    - Construct several subsequence automata (general, level-k, alphabet-aware)
    - Generate a valid and an invalid subsequence
    - Evaluate acceptance of both
    - Print automaton size statistics

This script does NOT modify the underlying automaton implementation.
It only adds I/O, sampling utilities, and clean reporting.
"""

import random
import sys
from typing import Set

from AlphabetAwareAutomaton import AlphabetAwareLevelAutomaton
from GeneralAutomaton import GeneralAutomaton
from LevelAutomaton import LevelAutomaton

# ---------------------------------------------------------------------------
# File utilities
# ---------------------------------------------------------------------------


def read_text_file(path: str) -> str:
    """
    Read an entire text file as a single string.

    Parameters
    ----------
    path : str
        Path to a UTF-8 encoded text file.

    Returns
    -------
    str
        The file contents with surrounding whitespace stripped.

    Raises
    ------
    SystemExit
        If the file is not found.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Subsequence generation helpers
# ---------------------------------------------------------------------------


def generate_valid_subsequence(s: str, length: int = 5) -> str:
    """
    Generate a random *valid* subsequence of the string.

    The function selects indices in sorted order, ensuring that the
    result is always a subsequence.

    Parameters
    ----------
    s : str
        Base string.
    length : int
        Maximum length of the subsequence.

    Returns
    -------
    str
        A valid subsequence.
    """
    if not s:
        return ""

    chosen = sorted(random.sample(range(len(s)), min(length, len(s))))
    return "".join(s[i] for i in chosen)


def generate_invalid_subsequence(s: str, alphabet: Set[str], length: int = 5) -> str:
    """
    Generate a guaranteed *invalid* subsequence.

    Strategy:
      1. Prefer characters NOT in the string ⇒ always invalid.
      2. If all alphabet characters appear in the string, create an
         impossible repetition pattern (e.g., too many copies of one symbol).

    Parameters
    ----------
    s : str
        Base string.
    alphabet : Set[str]
        Characters present in the base string.
    length : int
        Desired length of invalid subsequence.

    Returns
    -------
    str
        An invalid subsequence.
    """
    available_missing = list(set("abcdefghijklmnopqrstuvwxyz") - alphabet)

    if available_missing:
        # Use letters guaranteed NOT to appear in s
        return "".join(random.choice(available_missing) for _ in range(length))

    # If alphabet covers all letters: force too many occurrences of a character.
    c = random.choice(list(alphabet))
    return c * (s.count(c) + 3)  # impossible count


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------


def main() -> None:
    """
    Command-line entry point.

    Expects:
        python main.py <input.txt>

    The file is read, automata are built, and both a valid and invalid
    subsequence are tested.
    """
    if len(sys.argv) != 2:
        print("Usage: python main.py <input.txt>")
        sys.exit(1)

    filename = sys.argv[1]
    text = read_text_file(filename)

    if not text:
        print("ERROR: Input file is empty.")
        sys.exit(1)

    alphabet = set(text)

    # Generate testing subsequences
    valid = generate_valid_subsequence(text, max(1, len(text) // 3))
    invalid = generate_invalid_subsequence(text, alphabet)

    print("===================================================")
    print("Loaded text statistics")
    print("---------------------------------------------------")
    print("Original string length:", len(text))
    print("Alphabet size:", len(alphabet))
    print("Valid subsequence   :", valid)
    print("Invalid subsequence :", invalid)
    print("===================================================\n")

    # Create automata
    automata = [
        ("General Automaton (SA)", GeneralAutomaton(alphabet, text)),
        ("Level Automaton (k=2)", LevelAutomaton(alphabet, text, 2)),
        ("Level Automaton (k=3)", LevelAutomaton(alphabet, text, 3)),
        ("Level Automaton (k=5)", LevelAutomaton(alphabet, text, 5)),
        ("Level Automaton (k=50)", LevelAutomaton(alphabet, text, 50)),
        ("Alphabet-Aware Level Automaton", AlphabetAwareLevelAutomaton(alphabet, text)),
    ]

    # Run each automaton
    for name, aut in automata:
        print(name)
        print(aut.GetInfo())
        print("Valid subsequence accepted?   ", aut.Compute(valid))
        print("Invalid subsequence accepted? ", aut.Compute(invalid))
        print("===================================================\n")


if __name__ == "__main__":
    main()

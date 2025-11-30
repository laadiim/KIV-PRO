from typing import Dict, Set

from SubsequenceAutomaton import SubsequenceAutomaton


class GeneralAutomaton(SubsequenceAutomaton):
    """
    Standard subsequence automaton (SA) for a single string S.

    This implements the classic subsequence automaton (often called DASG),
    where each state `s` represents having matched up to position `s` in S.

    For each state s (0 ≤ s ≤ n) and each character c in the alphabet:
        transitionTable[s][c] = smallest t > s such that S[t] == c

    Properties
    ----------
    - Number of states: n + 1
    - Number of transitions: O(n * |alphabet|)

    This is the baseline against which the more compact default-transition
    automata are compared.
    """

    def __init__(self, alphabet: Set[str], string: str) -> None:
        """
        Construct the standard subsequence automaton for the given string.

        Parameters
        ----------
        alphabet : Set[str]
            Set of characters in the string (or superset).
        string : str
            The original string S used to build the automaton.
        """
        super().__init__()

        self._alphabet = alphabet
        self._originalString = string
        n = len(string)

        # Transition table for states 0..n
        # State numbers: 0..n; position in string: 1..n
        self._transitionTable = [{} for _ in range(n + 1)]

        # Nearest occurrence for each character when scanning backwards.
        # nearest[c] = lowest state index > current corresponding to next c.
        nearest: Dict[str, int | None] = {c: None for c in alphabet}

        # Build next-occurrence transitions backwards.
        # When we are at string index i (0-based), the "next occurrence"
        # is at state i+1 (since state indices correspond to prefix lengths).
        for i in range(n - 1, -1, -1):
            nearest[string[i]] = i + 1
            # At state i, we capture the snapshot of nearest for all characters.
            for c, pos in nearest.items():
                if pos is not None:
                    self._transitionTable[i][c] = pos

        # State n is a sink state: it has an empty transition dict.

    # ------------------------------------------------------------------ #
    # Matching (straight DFA run)                                       #
    # ------------------------------------------------------------------ #
    def Compute(self, inputStr: str) -> bool:
        """
        Run the DFA to test whether `inputStr` is a subsequence of S.

        Parameters
        ----------
        inputStr : str
            Candidate subsequence.

        Returns
        -------
        bool
            True if `inputStr` is a subsequence of the original string S,
            False otherwise.
        """
        state = 0  # start at prefix length 0

        for c in inputStr:
            # If the symbol is not in the known alphabet, reject immediately.
            if c not in self._alphabet:
                return False

            # If there is no outgoing transition for c, subsequence fails.
            if c not in self._transitionTable[state]:
                return False

            # Move to next state.
            state = self._transitionTable[state][c]

        return True

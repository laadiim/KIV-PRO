from typing import Dict, Set

from AutomatonData import AutomatonData
from SubsequenceAutomaton import SubsequenceAutomaton


class GeneralAutomaton(SubsequenceAutomaton):
    """
    Standard subsequence automaton (SA) for a single string S.
    Defined exactly as in the paper:
        State s represents matching up to position s in S.
        For each character c and state s,
        transition[s][c] = smallest t > s such that S[t] = c.
    """

    def __init__(self, alphabet: Set[str], string: str) -> None:
        super().__init__()

        self._alphabet = alphabet
        self._originalString = string
        n = len(string)

        # allocate transition table for states 0..n
        self._transitionTable = [{} for _ in range(n + 1)]

        # next-occurrence dictionary (for backward scan)
        # nearest[c] = next position where character c occurs
        nearest: Dict[str, int | None] = {c: None for c in alphabet}

        # Build next-occurrence lists backwards
        # State numbers correspond to 0..n.
        # String positions correspond to 1..n.
        # When we process i in 0-based string index,
        # the next-occurrence should be stored as state i+1.
        for i in range(n - 1, -1, -1):
            nearest[string[i]] = i + 1  # next occurrence of this char is state i+1
            # Store a snapshot of nearest into state i
            for c, pos in nearest.items():
                if pos is not None:
                    self._transitionTable[i][c] = pos

        # state n (end state) keeps an empty dictionary (no transitions)

    # -------------------------------------------------------------
    # Matching (straight DFA run)
    # -------------------------------------------------------------
    def Compute(self, inputStr: str) -> bool:
        state = 0  # start at prefix length 0

        for c in inputStr:
            if c not in self._alphabet:
                return False
            if c not in self._transitionTable[state]:
                return False
            state = self._transitionTable[state][c]

        return True

    # -------------------------------------------------------------
    # Size info
    # -------------------------------------------------------------
    def GetInfo(self) -> AutomatonData:
        vertexCount = len(self._transitionTable)
        edgeCount = sum(len(t) for t in self._transitionTable)
        return AutomatonData(vertexCount, edgeCount)

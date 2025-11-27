from math import ceil, log2
from typing import Dict, List, Set

from AutomatonData import AutomatonData
from SubsequenceAutomaton import SubsequenceAutomaton


class AlphabetAwareLevelAutomaton(SubsequenceAutomaton):
    """
    Implements the Alphabet-Aware Level Automaton from Section 3.2 of:
    'Subsequence automata with default transitions'
    by Bille, Gørtz & Skjoldjensen (2017).  :contentReference[oaicite:1]{index=1}

    Size:  O(n log σ)
    Delay: O(log σ)
    """

    _levels: List[int]

    def __init__(self, alphabet: Set[str], string: str) -> None:
        super().__init__()

        self._alphabet = alphabet
        self._originalString = string
        n = len(string)

        # Allocate transition table
        self._transitionTable = []

        # Precompute levels for states 0..n
        self._generateLevels()

        σ = len(alphabet)
        Lmax = ceil(log2(σ)) if σ > 1 else 0

        # nearest higher-level state tracking
        nearestLevelPos: List[int] = [n + 1] * (Lmax + 1)

        # nearest occurrence of each character (state number 1..n; n+1 means "none")
        nearestCharPos: Dict[str, int] = {c: n + 1 for c in alphabet}

        # Build automaton states backwards
        for s in range(n, -1, -1):

            lvl = self._levels[s]

            # Find next higher-level state
            next_level_state = n + 1
            for L in range(lvl + 1, Lmax + 1):
                if nearestLevelPos[L] < next_level_state:
                    next_level_state = nearestLevelPos[L]

            table: Dict[str, int] = {}

            # Default transition
            if next_level_state <= n:
                table["def"] = next_level_state

            # Span determines alphabet-aware rule
            span = next_level_state - s

            # ---------------------------------------------------------
            # REGULAR TRANSITIONS
            # ---------------------------------------------------------
            if span >= σ:
                # Alphabet-aware: include transitions for ALL characters
                for c in alphabet:
                    pos = nearestCharPos[c]
                    if 1 <= pos <= n and pos <= next_level_state:
                        table[c] = pos
            else:
                # Include only characters that occur before next_level_state
                for c, pos in nearestCharPos.items():
                    if 1 <= pos <= n and pos <= next_level_state:
                        table[c] = pos

            self._transitionTable.append(table)

            # Update nearest-level
            nearestLevelPos[lvl] = s

            # Update nearest-characters
            if s > 0:
                nearestCharPos[self._originalString[s - 1]] = s

        # reverse to get states 0..n in correct order
        self._transitionTable.reverse()

    # -------------------------------------------------------------
    # Level: min(log2 σ, largest x with i % 2^x == 0)
    # -------------------------------------------------------------
    def _generateLevels(self) -> None:
        n = len(self._originalString)
        σ = len(self._alphabet)
        Lmax = ceil(log2(σ)) if σ > 1 else 0

        self._levels = [0] * (n + 1)

        for i in range(1, n + 1):
            lvl = 0
            power = 2
            while lvl + 1 <= Lmax and i % power == 0:
                lvl += 1
                power *= 2
            self._levels[i] = lvl

    # -------------------------------------------------------------
    # SAD evaluation: follow default transitions until a match
    # -------------------------------------------------------------
    def Compute(self, inputStr: str) -> bool:
        state = 0

        for c in inputStr:
            if c not in self._alphabet:
                return False

            while True:
                table = self._transitionTable[state]

                # Regular match
                if c in table:
                    state = table[c]
                    break

                # Default transition
                if "def" in table:
                    state = table["def"]
                    continue

                # No match possible
                return False

        return True

    # -------------------------------------------------------------
    # Count states and transitions
    # -------------------------------------------------------------
    def GetInfo(self) -> AutomatonData:
        vertexCount = len(self._transitionTable)
        edgeCount = sum(len(t) for t in self._transitionTable)
        return AutomatonData(vertexCount, edgeCount)

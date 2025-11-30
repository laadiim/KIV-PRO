from math import ceil, log2
from typing import Dict, List, Set

from SubsequenceAutomaton import SubsequenceAutomaton


class AlphabetAwareLevelAutomaton(SubsequenceAutomaton):
    """
    Alphabet-aware level automaton (Section 3.2 in the paper):

        Bille, Gørtz & Skjoldjensen (2017),
        "Subsequence automata with default transitions",
        Journal of Discrete Algorithms.

    This is the k = 2 special case with an alphabet-aware optimization.

    Asymptotic properties
    ---------------------
    Size:  O(n log σ)
    Delay: O(log σ)

    Main idea
    ---------
    - States are assigned a "level" based on the largest power of 2 dividing
      the state index, but never exceeding ceil(log2 σ).
    - Default transitions move to the next state of strictly higher level.
    - If the span to the next higher-level state is large enough (≥ σ),
      we include transitions for all characters in the alphabet; otherwise
      we include only those that occur before the next higher-level state.
    """

    _levels: List[int]

    def __init__(self, alphabet: Set[str], string: str) -> None:
        """
        Build the alphabet-aware level automaton for the given string.

        Parameters
        ----------
        alphabet : Set[str]
            Alphabet of the original string.
        string : str
            Original string S.
        """
        super().__init__()

        self._alphabet = alphabet
        self._originalString = string
        n = len(string)

        # Allocate transition table (we will fill it backwards, then reverse).
        self._transitionTable = []

        # Precompute levels for states 0..n.
        self._generateLevels()

        σ = len(alphabet)
        Lmax = ceil(log2(σ)) if σ > 1 else 0

        # nearestLevelPos[L] = smallest state with level L that is > s
        nearestLevelPos: List[int] = [n + 1] * (Lmax + 1)

        # nearestCharPos[c] = closest occurrence of c as a state in [1..n],
        # n+1 means "none".
        nearestCharPos: Dict[str, int] = {c: n + 1 for c in alphabet}

        # Build automaton states backwards: s = n, n-1, ..., 0.
        for s in range(n, -1, -1):
            lvl = self._levels[s]

            # Find the next state with a strictly higher level.
            next_level_state = n + 1
            for L in range(lvl + 1, Lmax + 1):
                if nearestLevelPos[L] < next_level_state:
                    next_level_state = nearestLevelPos[L]

            table: Dict[str, int] = {}

            # Default transition (if a higher-level state exists).
            if next_level_state <= n:
                table["def"] = next_level_state

            # Span between this state and the next higher-level state
            # (n+1 if none exists).
            span = next_level_state - s

            # ---------------------------------------------------------
            # REGULAR TRANSITIONS
            # ---------------------------------------------------------
            if span >= σ:
                # Alphabet-aware rule: include transitions for *all* characters
                # in the alphabet, but only if they occur before next_level_state.
                for c in alphabet:
                    pos = nearestCharPos[c]
                    if 1 <= pos <= n and pos <= next_level_state:
                        table[c] = pos
            else:
                # Only include characters that actually occur before
                # the next higher-level state.
                for c, pos in nearestCharPos.items():
                    if 1 <= pos <= n and pos <= next_level_state:
                        table[c] = pos

            self._transitionTable.append(table)

            # Update nearest level for this state's level.
            nearestLevelPos[lvl] = s

            # Update nearest character positions (suffix-based).
            if s > 0:
                nearestCharPos[self._originalString[s - 1]] = s

        # Reverse table so indices correspond to states 0..n.
        self._transitionTable.reverse()

    # ------------------------------------------------------------------ #
    # Level: min(log2 σ, largest x with i % 2^x == 0)                    #
    # ------------------------------------------------------------------ #
    def _generateLevels(self) -> None:
        """
        Precompute the level for each state index 0..n.

        For i in [1..n]:
            level(i) = min(ceil(log2 σ), largest x such that i % 2^x == 0)

        State 0 is assigned level 0.
        """
        n = len(self._originalString)
        σ = len(self._alphabet)
        Lmax = ceil(log2(σ)) if σ > 1 else 0

        self._levels = [0] * (n + 1)

        for i in range(1, n + 1):
            lvl = 0
            power = 2

            # largest x with i % 2^x == 0, capped at Lmax
            while lvl + 1 <= Lmax and i % power == 0:
                lvl += 1
                power *= 2

            self._levels[i] = lvl

    # ------------------------------------------------------------------ #
    # SAD evaluation: follow default transitions until match             #
    # ------------------------------------------------------------------ #
    def Compute(self, inputStr: str) -> bool:
        """
        Evaluate whether `inputStr` is accepted by this SAD.

        For each character:
            - If it's not in the alphabet, reject.
            - Otherwise, follow explicit transitions if present.
            - If not, follow default transitions until either:
                * an explicit transition is found, or
                * no default exists → reject.

        Parameters
        ----------
        inputStr : str
            Candidate subsequence.

        Returns
        -------
        bool
            True if accepted, False otherwise.
        """
        state = 0

        for c in inputStr:
            # Characters not in the alphabet cannot be subsequences.
            if c not in self._alphabet:
                return False

            while True:
                table = self._transitionTable[state]

                # Try a regular transition match.
                if c in table:
                    state = table[c]
                    break

                # Otherwise, follow default if available.
                if "def" in table:
                    state = table["def"]
                    continue

                # No way forward for this character.
                return False

        return True

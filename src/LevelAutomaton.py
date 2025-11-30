from math import ceil, log
from typing import Dict, List, Set

from SubsequenceAutomaton import SubsequenceAutomaton


class LevelAutomaton(SubsequenceAutomaton):
    """
    Generalized level automaton with parameter k.

    This implements the construction from Section 3.3 ("Full trade-off") of
    Bille, Gørtz & Skjoldjensen: "Subsequence automata with default transitions"
    (Journal of Discrete Algorithms, 2017).

    Key idea
    --------
    - States are grouped into levels according to the largest power of k
      dividing their index.
    - Default transitions go to the next state with a strictly higher level.
    - The number of outgoing explicit transitions grows exponentially with
      the level (base k), giving a trade-off between size and delay.

    Parameters
    ----------
    k : int
        Base of the exponential growth in outdegree on default paths.
        1 < k ≤ σ (alphabet size) is required theoretically.

    Attributes
    ----------
    _k : int
        Level base parameter.
    _levels : List[int]
        Level for each state index 0..n.
    """

    _k: int
    _levels: List[int]

    def __init__(self, alphabet: Set[str], string: str, k: int) -> None:
        """
        Build a level automaton for the given string and parameter k.

        Parameters
        ----------
        alphabet : Set[str]
            Alphabet of the original string.
        string : str
            Original string S.
        k : int
            Parameter defining the level function (base of exponent).
        """
        super().__init__()

        self._alphabet = alphabet
        self._originalString = string
        self._k = k
        self._levels = []
        self._transitionTable = []

        # Precompute levels for all positions 0..n (depends on |alphabet| and k).
        self._generateLevels()

        n = len(self._originalString)

        # Maximum level Lmax = ceil(log_{k}(|alphabet|)).
        # This matches the generalized alphabet-aware construction.
        Lmax = ceil(log(len(alphabet), k))

        # nearestLevelPos[L] = smallest state index with level L that is > i
        # (filled in backwards).
        nearestLevelPos: List[int] = [n + 1] * (Lmax + 1)

        # nearestCharPos[c] = nearest occurrence of character c as a state index
        # (1..n, n+1 means "none seen yet").
        nearestCharPos: Dict[str, int] = {c: n + 1 for c in alphabet}

        # Build transition table backwards for states n..0.
        for i in range(n, -1, -1):
            lvl = self._levels[i]

            # Find next state with strictly higher level.
            next_level_state = n + 1
            for L in range(lvl + 1, Lmax + 1):
                if nearestLevelPos[L] < next_level_state:
                    next_level_state = nearestLevelPos[L]

            table: Dict[str, int] = {}

            # Default transition to the next higher-level state (if any).
            if next_level_state <= n:
                table["def"] = next_level_state

            # Regular transitions: only to positions <= next_level_state.
            # NOTE: The original implementation excludes transitions to state n
            # because of the `pos < n` condition. This behaviour is kept intact.
            for c, pos in nearestCharPos.items():
                if pos <= next_level_state and pos < n:
                    table[c] = pos

            self._transitionTable.append(table)

            # Update level-tracking.
            nearestLevelPos[lvl] = i

            # Update nearest occurrence of character at position i.
            if i > 0:
                nearestCharPos[self._originalString[i - 1]] = i

        # Reverse list so that index corresponds to state (0..n).
        self._transitionTable.reverse()

    # ------------------------------------------------------------------ #
    # Level generation per Section 3.3                                   #
    # ------------------------------------------------------------------ #
    def _generateLevels(self) -> None:
        """
        Precompute levels for each state index 0..n.

        For each i (1 ≤ i ≤ n), the level is:
            level(i) = largest x such that i % (k^x) == 0,
            but at most ceil(log_k(|alphabet|)).

        State 0 is assigned level 0 by construction.
        """
        n = len(self._originalString)
        Lmax = ceil(log(len(self._alphabet), self._k))

        self._levels = [0] * (n + 1)

        for i in range(1, n + 1):
            lvl = 0
            power = self._k

            # largest x with i % (k^x) == 0, bounded by Lmax
            while lvl + 1 <= Lmax and i % power == 0:
                lvl += 1
                power *= self._k

            self._levels[i] = lvl

    # ------------------------------------------------------------------ #
    # SAD evaluation: follow defaults until we can match a character     #
    # ------------------------------------------------------------------ #
    def Compute(self, inputStr: str) -> bool:
        """
        Evaluate whether `inputStr` is accepted by this SAD.

        The run proceeds as follows:
            - For each character, follow default transitions until either:
                * a matching explicit transition is found, or
                * no further default exists → reject.
            - Move along the matched explicit transition.
            - If all characters can be processed in this way, accept.

        Parameters
        ----------
        inputStr : str
            Candidate subsequence.

        Returns
        -------
        bool
            True if accepted, False otherwise.
        """
        activeState = 0

        for char in inputStr:
            # If char is outside the alphabet, it cannot be a subsequence.
            if char not in self._alphabet:
                return False

            while True:
                table = self._transitionTable[activeState]

                # Regular transition found.
                if char in table:
                    activeState = table[char]
                    break

                # Try following a default transition.
                if "def" in table:
                    activeState = table["def"]
                    continue

                # No regular, no default → no possible match.
                return False

        return True

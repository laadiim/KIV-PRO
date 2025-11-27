from math import ceil, log
from typing import Dict, List, Set

from AutomatonData import AutomatonData
from SubsequenceAutomaton import SubsequenceAutomaton


class LevelAutomaton(SubsequenceAutomaton):
    _k: int
    _levels: List[int]

    def __init__(self, alphabet: Set[str], string: str, k: int) -> None:
        super().__init__()

        self._alphabet = alphabet
        self._originalString = string
        self._k = k
        self._levels = []
        self._transitionTable = []

        # Precompute levels for all positions 0..n
        self._generateLevels()

        n = len(self._originalString)

        # next higher level positions (filled later backwards)
        Lmax = ceil(log(len(alphabet), k))
        nearestLevelPos: List[int] = [n + 1] * (Lmax + 1)

        # next occurrence of each char
        nearestCharPos: Dict[str, int] = {c: n + 1 for c in alphabet}

        # Build table backwards
        for i in range(n, -1, -1):

            lvl = self._levels[i]

            # find next state with higher level
            next_level_state = n + 1
            for L in range(lvl + 1, Lmax + 1):
                if nearestLevelPos[L] < next_level_state:
                    next_level_state = nearestLevelPos[L]

            table: Dict[str, int] = {}

            # default transition if exists
            if next_level_state <= n:
                table["def"] = next_level_state

            # regular transitions: only to positions <= next_level_state
            for c, pos in nearestCharPos.items():
                if pos <= next_level_state and pos < n:
                    table[c] = pos

            self._transitionTable.append(table)

            # update tables
            nearestLevelPos[lvl] = i
            if i > 0:
                nearestCharPos[self._originalString[i - 1]] = i

        # reverse to get states 0..n
        self._transitionTable.reverse()

    # -------------------------------------------------------------
    # Level generation per Section 3.3 of the paper
    # -------------------------------------------------------------
    def _generateLevels(self) -> None:
        n = len(self._originalString)
        Lmax = ceil(log(len(self._alphabet), self._k))

        self._levels = [0] * (n + 1)

        for i in range(1, n + 1):

            lvl = 0
            power = self._k

            # largest x with i % k^x == 0
            while lvl + 1 <= Lmax and i % power == 0:
                lvl += 1
                power *= self._k

            self._levels[i] = lvl

    def Compute(self, inputStr: str) -> bool:
        activeState = 0

        for char in inputStr:
            if char not in self._alphabet:
                return False

            while True:
                table = self._transitionTable[activeState]

                # match regular
                if char in table:
                    activeState = table[char]
                    break

                # try default
                if "def" in table:
                    activeState = table["def"]
                    continue

                # no regular, no default → reject
                return False

        return True

    def GetInfo(self) -> AutomatonData:
        vertexCount = len(self._transitionTable)

        edgeCount = 0
        for v in self._transitionTable:
            edgeCount += len(v.keys())

        return AutomatonData(vertexCount, edgeCount)

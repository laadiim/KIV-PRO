from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Set

from AutomatonData import AutomatonData


class SubsequenceAutomaton(ABC):
    """
    Abstract base class for subsequence automata.

    Each concrete subclass must implement `Compute`, which decides whether
    a given input string is a subsequence of the underlying original string.

    Attributes
    ----------
    _alphabet : Set[str]
        Set of characters used in the original string.
    _originalString : str
        The original string from which the subsequence automaton is built.
    _transitionTable : List[Dict[str, int]]
        Transition table for states 0..n, where each dictionary maps:
            - character -> next state index
            - optionally "def" -> default-transition state index
    """

    _alphabet: Set[str]
    _originalString: str
    _transitionTable: List[Dict[str, int]]

    # --------------------------------------------------------------------- #
    # Core interface                                                        #
    # --------------------------------------------------------------------- #
    @abstractmethod
    def Compute(self, inputStr: str) -> bool:
        """
        Check whether the given string is accepted by this subsequence automaton.

        Parameters
        ----------
        inputStr : str
            Candidate subsequence to test.

        Returns
        -------
        bool
            True if `inputStr` is a subsequence of the original string
            represented by this automaton, False otherwise.
        """
        raise NotImplementedError

    # --------------------------------------------------------------------- #
    # Size / statistics interface                                           #
    # --------------------------------------------------------------------- #
    def GetInfo(self) -> AutomatonData:
        """
        Compute statistics about the internal automaton representation.

        Iterates over all states in `_transitionTable` and counts:
            - number of states (vertices)
            - number of transitions (edges)
            - how many transitions are default vs explicit
            - relative ratios and saved size versus a full DFA

        The meaning of "full DFA" here is:
            states = vertexCount
            transitions = vertexCount * |alphabet|

        Returns
        -------
        AutomatonData
            A dataclass aggregating all these statistics.
        """
        vertexCount = 0
        edgeCount = 0
        defaultCount = 0
        explicitCount = 0

        for vertex in self._transitionTable:
            vertexCount += 1
            edgeCount += len(vertex.keys())

            if "def" in vertex.keys():
                # One default + remaining explicit transitions
                defaultCount += 1
                explicitCount += len(vertex.keys()) - 1
            else:
                # Only explicit transitions
                explicitCount += len(vertex.keys())

        # Note: no protection against division by zero is added,
        # to preserve the original behaviour exactly.
        defaultRatio = defaultCount / edgeCount
        explicitRatio = explicitCount / edgeCount
        savedRatio = 1 - edgeCount / ((vertexCount + 1) * len(self._alphabet))

        return AutomatonData(
            vertexCount,
            edgeCount,
            defaultCount,
            explicitCount,
            defaultRatio,
            explicitRatio,
            savedRatio,
        )

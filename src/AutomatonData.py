from dataclasses import dataclass


@dataclass
class AutomatonData:
    """
    Container for basic statistics about an automaton.

    Attributes
    ----------
    vertexCount : int
        Number of states in the automaton.
    edgeCount : int
        Number of transitions (including both default and explicit).
    defaultTranstions : int
        Number of default transitions. (Name kept for backwards compatibility.)
    explicitTransitions : int
        Number of non-default (regular) transitions.
    defaultRatio : float
        Fraction of transitions that are default transitions.
    explicitRatio : float
        Fraction of transitions that are explicit transitions.
    savedAgainstFull : float
        Proportion of transitions saved compared to a full DFA of size
        `vertexCount * |alphabet|`.

    The string representation is formatted for readability, with grouped
    thousands and nicely trimmed percentages.
    """

    vertexCount: int
    edgeCount: int
    defaultTranstions: int
    explicitTransitions: int
    defaultRatio: float
    explicitRatio: float
    savedAgainstFull: float

    def _fmt(self, n: int) -> str:
        """
        Format an integer with a thin grouping (space as thousands separator).

        Parameters
        ----------
        n : int
            Number to format.

        Returns
        -------
        str
            Human-friendly formatted string.
        """
        return f"{n:,}".replace(",", " ")

    def _fmt_float(self, x: float) -> str:
        """
        Format a float as a percentage with up to 4 decimal places,
        removing trailing zeros and decimal points when possible.

        Parameters
        ----------
        x : float
            Number to format.

        Returns
        -------
        str
            Nicely formatted floating-point string.
        """
        return f"{x:.4f}".rstrip("0").rstrip(".")

    def __str__(self) -> str:
        """
        Produce a multi-line, human-readable summary of the automaton statistics.

        Returns
        -------
        str
            Multi-line report on automaton size and ratios.
        """
        return (
            "Vertex count (no. of states):       "
            f"{self._fmt(self.vertexCount)}\n"
            "Edge count (no. of transitions):    "
            f"{self._fmt(self.edgeCount)}\n"
            "Default transitions:                "
            f"{self._fmt(self.defaultTranstions)}\n"
            "Explicit transitions:               "
            f"{self._fmt(self.explicitTransitions)}\n"
            "Default ratio:                      "
            f"{self._fmt_float(self.defaultRatio * 100)}%\n"
            "Explicit ratio:                     "
            f"{self._fmt_float(self.explicitRatio * 100)}%\n"
            "Saved against full automaton:       "
            f"{self._fmt_float(self.savedAgainstFull * 100)}%"
        )

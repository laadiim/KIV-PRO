from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Set

from AutomatonData import AutomatonData


class SubsequenceAutomaton(ABC):
    _alphabet: Set[str]
    _originalString: str

    _transitionTable: List[Dict[str, int]]

    @abstractmethod
    def Compute(inputStr: str) -> bool:
        pass

    @abstractmethod
    def GetInfo() -> AutomatonData:
        pass

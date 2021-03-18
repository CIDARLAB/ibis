"""
--------------------------------------------------------------------------------
Description:
Datastructure describing the various attributes of a boolean algebraic
operation.

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from dataclasses import dataclass
from enum import Enum


@dataclass
class InputSignal:
    """
    Attributes:
        label: String label for the input signal.
        on_value: Value when signal is 'on'
        off_value: Value when signal is 'off'
        binary_value: The (4-bit?) binary value of the input signal.
    """

    label: str
    on_value: float
    off_value: float
    binary_value: int = None

    def __len__(self):
        return 1

    def set_binary_value(self, binary_value: int):
        """
        Sets the binary value of the input signal.

        Args:
            binary_value: The binary value to set the input signal to.
        """
        self.binary_value = binary_value


class LogicFunction(Enum):
    """
    Enumeration of all possible boolean logic functions.
    """

    NOT = 0
    AND = 1
    OR = 2
    XOR = 3
    NAND = 4
    NOR = 5
    XNOR = 6
    INITIAL = 7

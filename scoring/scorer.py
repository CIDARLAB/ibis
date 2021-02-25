"""
--------------------------------------------------------------------------------
Description:
Scores a a genetic circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""


class AbstractBaseScoring:
    def __init__(self):
        self.output = 8

    def output(self):
        return self.output


# Public Methods in an Interface
#   - Every Solver has to have these.
# Private Methods
#   - Actually implement the base logic.
#   -
class ConcreteBaseScoring:
    def __color_score(self):
        # Iterates over the sequence, counts the colors, does math on colors?
        pass

    def output(self):
        return self.__color_score()

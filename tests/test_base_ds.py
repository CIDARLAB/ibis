"""
--------------------------------------------------------------------------------
Description:
Tests for our baseclasses.

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from ibis.scoring import (
    BaseScoring,
    BaseRequirement,
    CelloScoring,
)

from ibis.datastucture import (
    logic,
)

import pytest


class BadScoring(BaseScoring):
    pass


class BadRequirement(BaseRequirement):
    pass


class GoodScoring(BaseScoring):
    def score(self):
        pass

    def get_requirements(self):
        pass


class GoodRequirements(BaseRequirement):
    def validate(self):
        pass

    def get_required_inputs(self):
        pass


def test_scoring_and_requirements_interface():
    """
    If a scoring module does not implement the baseline features, it raises a
    TypeError.
    """
    GoodScoring()
    GoodRequirements()
    with pytest.raises(TypeError):
        BadScoring()
    with pytest.raises(TypeError):
        BaseRequirement()


if __name__ == "__main__":
    test_scoring_and_requirements_interface()

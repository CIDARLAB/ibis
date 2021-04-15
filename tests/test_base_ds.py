"""
--------------------------------------------------------------------------------
Description:
Tests for our baseclasses.

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import pathlib

from ibis.scoring import (
    BaseScoring,
    BaseRequirement,
    # CelloScoring,
)

from ibis.datastucture import (
    logic,
)
from ibis.ingress import parse_sbol_xml_tree
from ibis.datastucture import NetworkGeneticCircuit, NetworkGeneticNode

import pytest


@pytest.fixture
def get_input_and_gate():
    current_dir = pathlib.Path.cwd().parts[-1]
    # Assumes that you are running this file for testing.
    if current_dir == "tests":
        input_file = "test_cello/example_and_gate.xml"
    else:
        # Assumes you are running this at the top level.
        input_file = "tests/test_cello/example_and_gate.xml"
    return input_file


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


def test_scoring_and_requirements_interface(get_input_and_gate):
    """
    If a scoring module does not implement the baseline features, it raises a
    TypeError.
    """
    input_file = get_input_and_gate
    gc = parse_sbol_xml_tree(input_file)
    gn = NetworkGeneticCircuit(sbol_input=gc)
    req = GoodRequirements()
    GoodScoring(gn, req)
    with pytest.raises(TypeError):
        BadScoring(gn, req)
    with pytest.raises(TypeError):
        BaseRequirement()


def test_gc_calculation(get_input_and_gate):
    input_file = get_input_and_gate
    gc = parse_sbol_xml_tree(input_file)
    gn = NetworkGeneticCircuit(sbol_input=gc)
    # Should be approximately 48% GC Content
    assert round(gn.calculate_gc_content_percentage(), 2) == 0.48


if __name__ == "__main__":
    test_scoring_and_requirements_interface()

"""
--------------------------------------------------------------------------------
Description:


--------------------------------------------------------------------------------
"""

from ibis.datastucture import (
    NetworkGeneticCircuit,
)
from ibis.scoring.scorer import BaseRequirement, BaseScoring


class TemplateRequirement(BaseRequirement):
    def __init__(self):
        pass

    def get_required_inputs(self):
        pass

    def validate(self):
        pass


class TemplateScoring(BaseScoring):
    def __init__(
            self,
            network_graph: NetworkGeneticCircuit,
            requirement: TemplateRequirement,
    ):
        super().__init__(network_graph, requirement)

    def score(self):
        """
        Function to score efficacy of a gate.
        """
        return 42

    def get_requirements(self):
        return TemplateRequirement

    def report(self):
        print('Howdy.')

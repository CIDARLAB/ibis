'''
--------------------------------------------------------------------------------
Description:

Roadmap:

Written by W.R. Jackson <wrjackso@bu.edu>, DAMP Lab 2020
--------------------------------------------------------------------------------
'''
from collections import Counter

from ibis.datastucture import (
    NetworkGeneticNode,
    NetworkGeneticCircuit,
)

from ibis.scoring.scorer import BaseRequirement, BaseScoring

from rich.console import Console
from rich.table import Table

class AssemblyRequirement(BaseRequirement):
    def __init__(self):
        pass

    def get_required_inputs(self):
        pass

    def validate(self):
        pass

class AssemblyScoring(BaseScoring):
    """
    Assembly Scoring Metric:

    1- Fragment Length.
    2- GC Content
    3- Melt Temperature.
    """
    def __init__(
            self,
            network_graph: NetworkGeneticCircuit,
            requirement: AssemblyRequirement,
    ):
        super().__init__(network_graph, requirement)

    def score(self):
        pass

    def calculate_melt_temperature(self, input_node: NetworkGeneticNode):
        seq = input_node.sequence
        ctr = Counter(input_node.sequence)
        if len(seq) < 14:
            melt_temp = (ctr['A'] + ctr['T']) * 2 + (ctr['G'] + ctr['C']) * 4
        else:
            melt_temp = 64.9 + 41 * (ctr['G'] + ctr['C'] - 16.4) / (ctr['A'] + ctr['T'] + ctr['C'] + ctr['G'])
        return melt_temp

    def calculate_gc_content(self, input_node: NetworkGeneticNode):
        total_length = len(input_node.sequence)
        total_gc = sum(1 for bp in input_node.sequence if bp in 'CG')
        return total_gc/total_length

    @staticmethod
    def get_fragment_length(input_node: NetworkGeneticNode):
        return len(input_node.sequence)

    def get_requirements(self):
        return AssemblyRequirement

    def report(self):
        table = Table(title="Assembly Score (Parts)")
        table.add_column("Part Name", style="cyan", no_wrap=False)
        table.add_column("Part Type", style="green")
        table.add_column("Fragment Length")
        table.add_column("GC Content")
        table.add_column("Melt Temperature")
        for node in self.network_graph.get_nodes():
            table.add_row(
                f'{node.key_name}',
                f'{node.part_type}',
                f'{self.get_fragment_length(node)}',
                f'{self.calculate_gc_content(node)}',
                f'{self.calculate_melt_temperature(node)}'
            )
        console = Console()
        console.print(table)


"""
--------------------------------------------------------------------------------
Description:


--------------------------------------------------------------------------------
"""

from ibis.datastucture import (
    GeneticCircuit,
    LogicNetwork,
)
from ibis.scoring.scorer import BaseRequirement, BaseScoring

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

class BladeRequirement(BaseRequirement):
    """
    Built-in Blade module which predicts how well its circuits are likely to
    perform.

    Args:
        verilog_file_fp: <Absolute Filepath to Input Signal File>
        num_inputs: <Number of Inputs into Circuit>
        num_outputs: <Number of Outputs into Circuit>
        experimental_data_fp: <Filepath to experimental data>
        column_index: <Which vector column to extract from>
    """

    def __init__(
            self,
            verilog_file_fp: str,
            num_inputs: int,
            num_outputs: int,
            experimental_data_fp: str,
            column_index: int,
    ):
        self.verilog_file_fp = verilog_file_fp
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.experimental_data_fp = experimental_data_fp
        self.column_index = column_index

    def get_required_inputs(self):
        pass

    def validate(self):
        pass


class BladeScoring:
    def __init__(
            self,
            requirement: BladeRequirement,
    ):
        self.gc = GeneticCircuit(
            num_inputs=requirement.num_inputs,
            num_outputs=requirement.num_outputs,
        )
        self.verilog_file_fp = requirement.verilog_file_fp
        self.experimental_data_fp = requirement.experimental_data_fp
        self.logic_network = LogicNetwork(self.verilog_file_fp)
        self.truth_table = self.logic_network.generate_truth_table()
        self.gc.intended_truth_table = self.logic_network.generate_truth_vector(
            input_array=self.truth_table,
            output_index=0,
        )
        self.column_index = requirement.column_index
        self.binary_logic, self.gc.exp_data, self.true_angle = self.parse_blade_data()

    def parse_blade_data(self):
        cap_value = 20000.0
        with open(self.experimental_data_fp) as fp:
            lines = fp.readlines()
            query_line = lines[self.column_index+1].split(',') # Offset for Header.
            binary_logic = [int(x) for x in query_line[5:13]]
            exp_means = [float(x) if float(x) < cap_value else cap_value for x in query_line[13:21]]
            true_angle = float(query_line[29])
        return binary_logic, exp_means, true_angle

    def score(self):
        """
        Function to score efficacy of a gate.
        """
        return round(self.gc.vector_proximity(), 1)

    def get_requirements(self):
        return BladeRequirement

    def report(self):
        table = Table(title="Blade Score")
        for index, _ in enumerate(self.binary_logic):
            table.add_column(f'TT Vec Pos. {index}')
        table.add_column('Final Metric')
        table.add_row(
            f'{self.binary_logic[0]}',
            f'{self.binary_logic[1]}',
            f'{self.binary_logic[2]}',
            f'{self.binary_logic[3]}',
            f'{self.binary_logic[4]}',
            f'{self.binary_logic[5]}',
            f'{self.binary_logic[6]}',
            f'{self.binary_logic[7]}',
            f'{self.score()}°',
        )
        console = Console()
        console.print(table)



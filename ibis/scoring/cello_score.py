"""
--------------------------------------------------------------------------------
Description:

Roadmap:

Written by W.R. Jackson <wrjackso@bu.edu>, DAMP Lab 2020
--------------------------------------------------------------------------------
"""
import itertools
import math
from typing import (
    Callable,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import ticker

from ibis.datastucture import (
    NetworkGeneticCircuit,
    LogicNetwork,
    parse_cello_input_file,
)
from ibis.scoring.scorer import BaseRequirement, BaseScoring


class CelloRequirement(BaseRequirement):
    """
    Built-in Cello module which predicts how well its circuits are likely to
    perform.

    Args:
        ucf_fp: <Absolute Filepath to User Constraint File>
        input_signal_fp: <Absolute Filepath to Input Signal File>
        output_signal_fp: <Absolute Filepath to Output Signal File>
        verilog_file_fp: <Absolute Filepath to Input Signal File>
    """

    def __init__(
            self,
            ucf_fp: str = None,
            input_signal_fp: str = None,
            output_signal_fp: str = None,
            verilog_file_fp: str = None,
    ):
        self.ucf_fp = ucf_fp
        self.input_signal_fp = input_signal_fp
        self.output_signal_fp = output_signal_fp
        self.verilog_file_fp = verilog_file_fp

    def get_required_inputs(self):
        pass

    def validate(self):
        pass


class CelloScoring(BaseScoring):
    def __init__(
            self,
            network_graph: NetworkGeneticCircuit,
            requirement: CelloRequirement,
    ):
        super().__init__(network_graph, requirement)
        self.ucf_fp = requirement.ucf_fp
        self.input_signal_fp = requirement.input_signal_fp
        self.output_signal_fp = requirement.output_signal_fp
        self.verilog_file_fp = requirement.verilog_file_fp

        self.input_sensors = parse_cello_input_file(self.input_signal_fp)
        self.logic_network = LogicNetwork(self.verilog_file_fp)

    def score(self):
        """
        Function to score efficacy of a gate.
        """
        logical_inputs = list(
            itertools.product(
                [True, False],
                repeat=len(self.logic_network.get_available_inputs())
            )
        )
        high_off = float("-inf")
        low_on = float("inf")
        # We basically iterate over all possibilities of the truth table.
        for logical_input in logical_inputs:
            truth = self.logic_network.get_logical_output(logical_input)
            input_list = list(self.input_sensors.sensor_table.keys())[:len(logical_input)]
            boolean_input = {
                input_list[0]: logical_input[0],
                input_list[1]: logical_input[1],
            }
            on_value, off_value = self.input_sensors.generate_score_for_sensor(
                boolean_input
            )
            # If this is True, our signal is high. If it is False, our signal
            # is low. We use this to get the lowest one and highest off
            # respectively.
            if truth:
                if on_value < low_on:
                    low_on = on_value
            if not truth:
                if off_value > high_off:
                    high_off = off_value
        return math.log10(high_off / low_on)

    def get_requirements(self):
        return CelloRequirement


# ------------------------ Publicly Available Functions ------------------------
def graph_response_function(
        func: Callable,
        start: int = 0.001,
        stop: int = 1000,
        number_of_observations: int = 1000000,
):
    """
    Generates a graph for the passed in function in the same style as the log
    based graphs in the assignment.

    Args:
        func: The function to graph.
        start: At what point to start the graph
        stop: At what point to stop the graph.
        number_of_observations: Number of observations to plot. Given the
            curvature of the sigmoidal functions, a very high observation
            count is recommended, or you will end up with angular graphs.
    """
    x = np.linspace(start, stop, number_of_observations)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim([0.001, 1000])
    ax.set_ylim([0.001, 1000])
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%0.3f"))
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%0.3f"))
    plt.plot(x, list(map(func, x)))
    plt.show()


if __name__ == "__main__":
    thing = CelloRequirement()
    thing.get_description()

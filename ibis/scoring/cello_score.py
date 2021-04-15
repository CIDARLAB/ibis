"""
--------------------------------------------------------------------------------
Description:

Roadmap:

Written by W.R. Jackson <wrjackso@bu.edu>, DAMP Lab 2020
--------------------------------------------------------------------------------
"""
import copy
from functools import partial
import itertools
from pathlib import Path
from typing import (
    Callable,
    List,
    Union,
    Tuple,
)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
import scipy.optimize as opt

from ibis.datastucture.logic import InputSignal, LogicFunction
from ibis.datastucture.circuits import NetworkGeneticCircuit
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
        ucf_fp: Path = None,
        input_signal_fp: Path = None,
        output_signal_fp: Path = None,
        verilog_file_fp: Path = None,
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

    def score(self):
        for node in self.network_graph.graph.nodes:
            print(node)

    def get_requirements(self):
        return CelloRequirement


class CelloRepressor:
    def __init__(
        self,
        n: float,
        k: float,
        y_min: float,
        y_max: float,
        number_of_inputs: int,
    ):
        """

        Args:
            n: Slope of the sigmoidal curve that defines the response function
            k: The distance between zero to the mid-point of the max slope of
                the x-axis
            y_min: The minimum y value
            y_max: The maximum y value
        """
        self.n: float = n
        self.k: float = k
        self.y_max: float = y_max
        self.y_min: float = y_min
        self.number_of_inputs: int = number_of_inputs

        # Attributes related to counting the number of 'edits' done to the
        # repressor.
        self.dna_edits: int = 0
        self.protein_edits: int = 0

        # Attributes related to the biological input/output of the Repressor.
        # Inputs can be represented by either a dataclass representing the high
        # and low signal inputs to the repressor, or another repressor. The
        # output signal of those repressors is calculated recursively.
        self.biological_inputs: List[Union[CelloRepressor, Tuple[float, float]]] = []
        self.biological_output: int = 0

        # Attributes related to the logical input/output to the Repressor.
        self.logical_function: LogicFunction = LogicFunction.INITIAL
        self.logical_output: bool = None
        self.logical_inputs: [List[Union[int, CelloRepressor]]] = None

    def calculate_response_function(self) -> float:
        """
        Calculates the response function of the repressor as per the equation
        on page 3 of the homework. The repressor calculation looks like:

                                ymax - ymin
                    y = ymin + -------------
                                1.0 + (x/K)ⁿ

        Definitions for the variables of this function can be found in the
        class attribute definition.

        Returns:
            The biological output of the circuit
        """
        current_x = 0
        signal_index = 1 if self.get_logical_output() else 0
        for index, input_signal in enumerate(self.biological_inputs):
            if type(input_signal) is CelloRepressor:
                current_x += input_signal.calculate_response_function()
            if type(input_signal) is tuple:
                current_x += input_signal[signal_index]
            if type(input_signal) is InputSignal:
                if signal_index:
                    current_x += input_signal.on_value
                else:
                    current_x += input_signal.off_value
        self.biological_output = self.y_min + (
            (self.y_max - self.y_min) / (1.0 + (current_x / self.k) ** self.n)
        )
        return self.biological_output

    def set_biological_inputs(
        self,
        biological_inputs: List[
            Union[Tuple[float, float], "CelloRepressor", InputSignal]
        ],
    ):
        """
        Sets the biological inputs to the repressor.

        Args:
            biological_inputs: A list of biological inputs to the repressor.

        """
        if len(self.biological_inputs) + 1 > self.number_of_inputs:
            raise RuntimeError("Too many inputs into gate.")
        input_list = []
        for chemical_input in biological_inputs:
            if type(chemical_input) == Tuple:
                input_list.append(
                    InputSignal(
                        label="N/A",  # Possibly bad form. I think you'd have a db
                        # backing this in production that would probably have all
                        # signals predefined.
                        off_value=chemical_input[0],
                        on_value=chemical_input[1],
                    )
                )
            if (
                type(chemical_input) == CelloRepressor
                or type(chemical_input) == InputSignal
            ):
                input_list.append(chemical_input)
        self.biological_inputs.extend(biological_inputs)

    def set_logical_inputs(
        self,
        logical_inputs: List[Union[int, "CelloRepressor"]],
    ):
        """
        Sets the logical inputs to the repressor. This can either be via a
        adding another repressor where the logical output of that repressor
        will be calculated when called or setting a binary integer value.
        Binary values are prefixed with `0b****` for the purpose of conveying
        easily readable boolean gate logic.

        Args:
            logical_inputs: A list of logical inputs to the repressor.

        """
        self.logical_inputs = logical_inputs

    def set_logical_function(self, logical_function: str):
        """
        Sets the logical function of the repressor. In all documentation I've
        only seen NOT and NOR as possible operations, but I've added all
        boolean functions here in case this is just a simplified abstraction.

        Args:
            logical_function: String name correlating to the boolean function.
        """
        # There's an argument to be made here that's a bit silly and the
        # caller could just directly reference the enumerated logic value,
        # but I don't like the extra cognitive overhead.
        if logical_function == "AND":
            self.logical_function = LogicFunction.AND
        elif logical_function == "NOT":
            self.logical_function = LogicFunction.NOT
        elif logical_function == "OR":
            self.logical_function = LogicFunction.OR
        elif logical_function == "XOR":
            self.logical_function = LogicFunction.XOR
        elif logical_function == "NAND":
            self.logical_function = LogicFunction.NAND
        elif logical_function == "NOR":
            self.logical_function = LogicFunction.NOR
        elif logical_function == "XNOR":
            self.logical_function = LogicFunction.XNOR
        else:
            raise RuntimeError(
                f"Passed in Logical Function {logical_function} not defined."
            )

    def get_input_signal_total(self) -> float:
        """
        Convenience method for getting all input signals into the repressor. We
        add the value of all inputs to get the value of the singal into the
        repressor.

        I don't think you can have more than two inputs but y'know.

        Returns:
            Total input signal to all repressors.

        """
        return sum(self.get_input_signals())

    def get_input_signals(self) -> List[float]:
        """
        Gets all input signals into the repressor.

        Returns:
            A list of all input signals into the repressor. All inputs will be
            resolved into floats.
        """
        computed_input_signals = []
        for input_signal in self.biological_inputs:
            if type(input_signal) == CelloRepressor:
                computed_input_signals.append(input_signal.get_logical_output())
            else:
                computed_input_signals.append(input_signal)
        return computed_input_signals

    def get_logical_output(self):
        """
        Gets the logical output of the repressor.

        Returns:
            The logical output of the repressor.
        """
        computed_input_signals = []
        for input_signal in self.logical_inputs:
            if type(input_signal) == CelloRepressor:
                computed_input_signals.append(input_signal.get_logical_output())
            else:
                computed_input_signals.append(input_signal)
        if self.logical_function == LogicFunction.INITIAL:
            raise RuntimeError("Logical Function has not been set.")
        if self.logical_function == LogicFunction.NOT:
            if len(computed_input_signals) > 1:
                raise RuntimeError("Cannot NOT multiple inputs.")
            else:
                return ~computed_input_signals[0] & 0xF
        if len(computed_input_signals) != 2:
            raise RuntimeError("Need two binary inputs to perform logical operations")
        if self.logical_function == LogicFunction.AND:
            return (computed_input_signals[0] & computed_input_signals[1]) & 0xF
        if self.logical_function == LogicFunction.OR:
            return (computed_input_signals[0] | computed_input_signals[1]) & 0xF
        if self.logical_function == LogicFunction.XOR:
            return (computed_input_signals[0] ^ computed_input_signals[1]) & 0xF
        if self.logical_function == LogicFunction.NAND:
            return (~(computed_input_signals[0] & computed_input_signals[1])) & 0xF
        if self.logical_function == LogicFunction.NOR:
            return (~(computed_input_signals[0] | computed_input_signals[1])) & 0xF
        if self.logical_function == LogicFunction.XNOR:
            return (~(computed_input_signals[0] ^ computed_input_signals[1])) & 0xF

    def get_linear_coefficients(self) -> List[float]:
        """
        Utility function to turn a Repressor into it's coefficients for the
        purpose of visualization.

        Returns:
            A list of all linear coefficients which define the response function
            of a repressor.
        """
        return [self.y_min, self.y_max, self.k, self.n]

    def get_coefficients(self) -> np.ndarray:
        """
        Utility function to turn a repressor into it's coefficients for the
        purpose of optimization.

        Returns:
            A numpy array of coefficients for the repressor. These are
            represented by an ndarray of float64 to avoid floating point
            error.
        """
        return np.asarray(
            [
                self.get_input_signal_total(),
                self.y_min,
                self.y_max,
                self.k,
                self.n,
            ]
        ).astype(np.float64)

    def score_self(self, score_table: bool = False):
        """
        Function to score efficacy of a gate.
        """
        df = pd.DataFrame(columns=["logical_input", "biological_input", "response"])
        logical_inputs = list(
            itertools.product([0b0000, 0b1111], repeat=self.number_of_inputs)
        )
        high_off = float("-inf")
        low_on = float("inf")
        for logical_input in logical_inputs:
            self.set_logical_inputs([x for x in logical_input])
            if self.number_of_inputs > 1:
                for index, biological_input in enumerate(self.biological_inputs):
                    if type(biological_input) == CelloRepressor:
                        biological_input.set_logical_inputs([logical_input[index]])
            response = self.calculate_response_function()
            # If this is True, our signal is high. If it is False, our signal
            # is low. We use this to get the lowest one and highest off
            # respectively.
            if self.get_logical_output():
                if response < low_on:
                    low_on = response
            if not self.get_logical_output():
                if response > high_off:
                    high_off = response
            if score_table:
                df_dict = {
                    "logical_input": logical_input,
                    "biological_input": str(self.get_input_signals()),
                    "response": self.calculate_response_function(),
                }
                df = df.append(df_dict, ignore_index=True)
        if score_table:
            print(df)
        return np.log10(high_off / low_on)


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


def optimize_repressor(
    input_repressor: CelloRepressor,
    optimization_method: str,
    bio_optimization: str = "DNA",
):
    """
    Monolithic entrypoint and wrapper around the optimization functionality
    of Scipy.

    I will freely admit my ignorance on the benefits and drawbacks of many of
    these optimization algorithms.

    Args:
        input_repressor: The input to optimize.
        optimization_method: Which optimization method to use, either through
            a global optimization method or through
        bio_optimization: What parts of the repressor optimize.

    Returns:

    """
    if bio_optimization == "DNA":
        curried_optimize = partial(
            optimizable_response_function_dna,
            input_repressor=input_repressor,
        )
        variable_count = 2
    if bio_optimization == "ALL":
        curried_optimize = partial(
            optimizable_response_function_dna_and_protein,
            input_repressor=input_repressor,
        )
        variable_count = 4
    # Scipy Global optimization methods have a different interface than
    # the standard minimize.
    if optimization_method in [
        "dual_annealing",
        "basin-hopping",
        "differential-evolution",
        "shgo",
        "brute",
    ]:
        bounds_list = []
        # I assume that practically messing with the ymin and ymax of a
        # repressor has some sort of bound, but it's not detailed in the
        # assignment. If you look at the UCF the maximum y max is 6.8, so lets
        # call it ten?
        bounds_list.append([0.0, 10.0])
        # Same with K bounds, going for something higher than what is seen
        # in the standard e-coli UCF.
        bounds_list.append([0, 0.5])
        if bio_optimization == "ALL":
            # Stretching can be 0:1.5
            bounds_list.append([0, 1.5])
            bounds_list.append([0, 1.05])
        # Avg Run Time: 6000ms
        if optimization_method == "dual_annealing":
            return opt.dual_annealing(
                curried_optimize,
                bounds=bounds_list,
            )
        # Avg Run Time: 4800ms
        if optimization_method == "basin-hopping":
            return opt.basinhopping(curried_optimize, [1] * variable_count)
        # Avg Run Time: 195ms
        if optimization_method == "differential-evolution":
            return opt.differential_evolution(
                curried_optimize,
                bounds=bounds_list,
            )
        # Avg Run Time: 9ms, but fails to actually converge to anything useful.
        # Upon casual research into the field of optimization, it's probably
        # my initial conditions.
        if optimization_method == "shgo":
            return opt.shgo(
                curried_optimize,
                bounds=bounds_list,
            )
        # Avg Run Time: 76ms.
        if optimization_method == "brute":
            return opt.brute(
                curried_optimize,
                ranges=bounds_list,
            )
    elif optimization_method in [
        "Nelder-Mead",
        "Powell",
        "CG",
        "BFGS",
        "Newton-CG",
        "L-BFGS-B",
        "TNC",
        "COBYLA",
        "SLSQP",
        "trust-constr",
        "dogleg",
        "trust-ncg",
        "trust-krylov",
        "trust-exact",
    ]:
        return opt.minimize(
            curried_optimize,
            [1] * variable_count,
            method=optimization_method,
        )
    else:
        raise RuntimeError(
            f"Unable to find requested optimization method " f"{optimization_method}"
        )


def optimizable_response_function_dna(x, input_repressor: CelloRepressor) -> float:
    """
    Alters the linear coefficents that determine the score of a repressor and
    returns the new value. Used for optimization.

    Args:
        x: x0, x1 corresponding to changes in [ymin, ymax] and k respectively.
        input_repressor: Repressor to optimize.

    Returns:
        The score of the change repressor.
    """
    # First variable corresponds to changing y_min and y_max
    # Second variable corresponds to altering the RBS
    x0, x1 = x
    input_repressor = copy.deepcopy(input_repressor)
    input_repressor.y_min = input_repressor.y_min * x0
    input_repressor.y_max = input_repressor.y_max * x0
    input_repressor.k = input_repressor.k * x1
    # The negative sign is so we minimize a negative value, so we end up
    # maximizing the function.
    return -input_repressor.score_self()


def optimizable_response_function_dna_and_protein(
    x, input_repressor: CelloRepressor
) -> float:
    """
    Alters the linear coefficents that determine the score of a repressor and
    returns the new value. Used for optimization.

    Args:
        x: x0, x1 corresponding to changes in [ymin, ymax] and k respectively.
        input_repressor: Repressor to optimize.

    Returns:
        The score of the change repressor.
    """
    # First variable corresponds to changing y_min and y_max
    # Second variable corresponds to altering the RBS
    # Third variable corresponds to stretching the sigmoid
    # Fourth variable corresponds to changing the slope
    (
        x0,
        x1,
        x2,
        x3,
    ) = x
    input_repressor = copy.deepcopy(input_repressor)
    # DNA
    input_repressor.y_min = input_repressor.y_min * x0
    input_repressor.y_max = input_repressor.y_max * x0
    input_repressor.k = input_repressor.k * x1
    # Protein
    input_repressor.y_max = input_repressor.y_max * x2
    input_repressor.y_min = input_repressor.y_min / x2
    input_repressor.n = input_repressor.n * x3
    # The negative sign is so we minimize a negative value, so we end up
    # maximizing the function.
    return -input_repressor.score_self()


def simple_calculate_response_function(x, coefficients: list) -> float:
    """
    Simple response function calculation for value of x. Designed to be
    used in tandem with 'get_linear_coefficents' method of Repressor Gates.

    Args:
        x: Input signal value.
        coefficients: Linear coefficients. (ymin, ymax, k, n)

    Returns:
        The response function of the repressor.

    """
    y_min, y_max, k, n = map(np.float64, coefficients)
    return y_min + ((y_max - y_min) / (1.0 + (x / k) ** n))


if __name__ == "__main__":
    thing = CelloRequirement()
    thing.get_description()

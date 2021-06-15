"""
--------------------------------------------------------------------------------
Description:
Functionality related to parsing verilog and generating logical networks.

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from dataclasses import dataclass
import os
import itertools
from typing import (
    Callable,
    Optional,
    Union,
    List,
    Dict,
    Tuple,
)

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

from pyverilog.vparser.parser import parse


# ----------------------------- LOGICAL FUNCTIONS ------------------------------
def string_to_logic_function(function_name: str) -> Callable:
    """
    Converts a string name of a logic function to its logical equivalent.

    Args:
        function_name: The name of the function

    Returns:
        Non-evaluated logic function.

    """
    function_name = function_name.upper()
    function_lut = {
        "WIRE": WIRE,
        "NOT": NOT,
        "AND": AND,
        "OR": OR,
        "XOR": XOR,
        "NAND": NAND,
        "NOR": NOR,
        "XNOR": XNOR,
    }
    return function_lut[function_name]


def WIRE(input_a: bool):
    return input_a


def NOT(input_a: bool):
    return ~input_a


def AND(input_a: bool, input_b: bool):
    return input_a & input_b


def OR(input_a: bool, input_b: bool):
    return input_a | input_b


def XOR(input_a: bool, input_b: bool):
    return input_a ^ input_b


def NAND(input_a: bool, input_b: bool):
    return ~(input_a & input_b)


def NOR(input_a: bool, input_b: bool):
    return ~(input_a | input_b)


def XNOR(input_a: bool, input_b: bool):
    return ~(input_a ^ input_b)


# --------------------------------- LOGIC NODE ---------------------------------
class LogicNode:
    def __init__(
            self,
            boolean_value: Optional[bool] = None,
            input_signals: Optional[List["LogicNode"]] = None,
            output_signal: Optional["LogicNode"] = None,
            node_name: Optional[str] = "temp",
            logical_function: Callable = None,
    ):
        """
        A logic node represents a node in our functional equivalent of a
        netlist. That means that a singular node can represent either an
        input signal, a boolean gate, or the final output of the circuit.

        Args:
            boolean_value: Represents the boolean return of the node
                (True | False)
            input_signals: A list of other LogicNodes that represent the
                inputs into this node.
            output_signal: The LogicNode that is fed the output of this node.
                This design presupposes that we do not have any form of fanout
                in our systems.
            node_name: Name of the node. Used as a handle to retrieve or filter
                nodes, typically.
            logical_function: If the node is a boolean gate, this represents
                the operation performed.
        """
        self.boolean_value = boolean_value
        self.input_signals = input_signals
        self.output_signal = output_signal
        self.node_name = node_name
        self.logical_function = logical_function
        self.node_rank = None


# ------------------------------- CIRCUIT NETWORK ------------------------------
@dataclass
class LogicNetwork:
    def __init__(self, verilog_fp: str):
        """
        A CircuitNetwork represents the boolean logic of the passed in verilog
        file. This class is responsible for parsing the verilog file and
        simulating the logic of the electrical circuit.

        Args:
            verilog_fp:
        """
        self.verilog_fp = verilog_fp
        if not os.path.isfile(verilog_fp):
            raise RuntimeError(
                f"Unable to locate file {verilog_fp}, please investigate."
            )
        self.input_signal_node_list = []
        self.output_signal_node_list = []
        self.function_counter = {}
        self.graph = nx.DiGraph()
        self.simple_graph = nx.DiGraph()
        self.cleanup()
        self.parse_verilog_file()

    # -------------------------- GETTERS AND SETTERS ---------------------------
    def add_node(self, node: LogicNode):
        """
        Adds a node to the network. Just a wrapper to simplify the code.

        Args:
            node: The node to add to the network.
        """
        if node.logical_function is not None:
            if node.logical_function.__name__ not in self.function_counter:
                self.function_counter[node.logical_function.__name__] = 1
            else:
                self.function_counter[node.logical_function.__name__] += 1
        if node.node_name == 'temp':
            f_name = node.logical_function.__name__
            f_index = self.function_counter[node.logical_function.__name__]
            node.node_name = f'{f_name}{f_index}'.upper()
        self.graph.add_node(node, node_name=node.node_name)

    def add_input_node(self, node: LogicNode):
        """
        Adds an input node.

        Args:
            node: The node to add to the network and input node list.
        """
        self.input_signal_node_list.append(node)

    def add_output_node(self, node: LogicNode):
        """
        Adds an output node.

        Args:
            node: The node to add to the network and output node list.
        """
        self.output_signal_node_list.append(node)

    def add_edge(self, start_node: LogicNode, end_node: LogicNode):
        """
        Adds an edge between two nodes.

        Args:
            start_node: Starting Node.
            end_node: Ending Node.
        """
        self.graph.add_edge(start_node, end_node)

    def get_node_by_node_name(self, name: str) -> LogicNode:
        """
        Get's a node by it's name. We do not currently enforce unique labels
        for each individual node, so be careful.

        Args:
            name: Name of the requested node.

        Returns:
            LogicNode: The requested node.
        """
        for node in self.graph.nodes:
            if node.node_name == name:
                return node

    def get_available_inputs(self) -> List[str]:
        """
        Returns a list of input node *names*, primarily to inform you
        of what inputs you can set when trying to get the logical output
        of the circuit.

        Returns:
            A list of input node names.

        """
        out_list = []
        # We assume that each of these have a name.
        for node in self.input_signal_node_list:
            out_list.append(node.node_name)
        return out_list

    def get_available_outputs(self):
        """
        Returns a list of output node *names*, primarily to inform you
        of what inputs you can set when trying to get the logical output
        of the circuit.

        Returns:
            A list of output node names.

        """
        out_list = []
        # We assume that each of these have a name.
        for node in self.output_signal_node_list:
            out_list.append(node.node_name)
        return out_list

    def get_number_of_inputs(self):
        return len(self.input_signal_node_list)

    def get_number_of_outputs(self):
        return len(self.output_signal_node_list)

    # ------------------------------- PARSING ----------------------------------

    def parse_verilog_file(
            self,
    ):
        """
        Uses Pyverilog (https://github.com/PyHDI/Pyverilog) to parse input
        verilog files into a networkx datastructure. This is kinda hacky for
        now, and should get expanded as we start to handle more complex
        circuits.
        """
        # Note the list containing the filepath. This will give you a very
        # confusing error message if not wrapped in an iterable even though
        # there documentation and code make it very clear you should be able to
        # do both.
        ast, directives = parse(
            [self.verilog_fp],
            preprocess_include=[],
            preprocess_define=[],
        )
        # We're only doing sequential logic for this first iteration for a
        # variety of reasons. I need to understand higher-level standards
        # within the hardware description field before I go too ham on this.
        # --
        # A number of verilog files can be joined by specifying a higher level
        # 'top' module that describes the relationships between each submodule.
        # This works much like a header in C++. As we are doing a single module
        # for this initial pass, we'll always default to the initial definition
        # position
        # TODO: I think the internals get jumbled depending on the circuit. This
        # below statement only works for struct, for example.
        for port in ast.description.definitions[0].portlist.ports:
            node_type = type(port.first).__name__
            node = LogicNode(node_name=port.first.name)
            self.add_node(node)
            if node_type == "Input":
                self.add_input_node(node)
            if node_type == "Output":
                self.add_output_node(node)
        for item in ast.description.definitions[0].items:
            # At this point each item composes either a declaration, or an
            # assignment. A declaration can just be the instantiation of an
            # input, and an assignment is typically taking a series of inputs
            # and applying a boolean function to them.
            if type(item).__name__ == "Decl":
                # Unsure if other ways of wire declaration will work. I think
                # this might also cause a presumption on the implicit ordering
                # of the input nodes into the circuit.
                if len(item.list) > 1:
                    for wire in item.list:
                        node = LogicNode(
                            node_name=wire.name,
                            logical_function=string_to_logic_function('WIRE'),
                        )
                        self.add_node(node)
                else:
                    node_attribute = item.list[0]
                    node_type = type(node_attribute).__name__
                    node = LogicNode(node_name=node_attribute.name)
                    self.add_node(node)
                    if node_type == "Input":
                        self.add_input_node(node)
                    if node_type == "Output":
                        self.add_output_node(node)
            # This is for something like a not gate.
            if type(item).__name__ == "InstanceList":
                node_attribute = item.instances[0]
                node_logical_function = string_to_logic_function(
                    node_attribute.module,
                )
                temp_node = LogicNode(logical_function=node_logical_function)
                self.add_node(temp_node)
                # I know that this is wrong. Need to figure out a way to
                # discern, it's not within the datastructure. Might have to
                # sort them in some capacity. I think given the fact that you
                # know the logical structure of it based on the string key,
                # you could presume some things and always be right.
                output = item.instances[0].portlist[0]
                inputs = item.instances[0].portlist[1:]
                for logical_input in inputs:
                    start_node = self.get_node_by_node_name(logical_input.argname.name)
                    self.add_edge(start_node, temp_node)
                output_node = self.get_node_by_node_name(output.argname.name)
                self.add_edge(temp_node, output_node)

                # start_node = None
                # out_node = None
                # for port in node_attribute.portlist:
                #     if port.argname.name in self.get_available_inputs():
                #         start_node = self.get_node_by_node_name(port.argname.name)
                #     if port.argname.name in self.get_available_outputs():
                #         out_node = self.get_node_by_node_name(port.argname.name)
                #     else:
                #         # This will label not gates with their respective out
                #         # wire labels. It might not be ok.
                #         temp_node.node_name = port.argname.name
                # if start_node is None:
                #     self.add_edge(temp_node, out_node)
                # if out_node is None:
                #     self.add_edge(start_node, temp_node)
            if type(item).__name__ == "Assign":
                input_attributes = item.right.var
                # Special class names in pyyosys that correlate to logical
                # functions. e.g., 'Or', 'And', etc etc.
                node_logical_function = string_to_logic_function(
                    str(type(input_attributes).__name__)
                )
                instantiated_node = LogicNode(logical_function=node_logical_function)
                self.add_node(instantiated_node)
                # Should be the 'further' node in the network as it was just
                # added. Might want to think about extending this to have
                #
                ref_node = list(self.graph.nodes.items())[-1][0]
                # TODO: How does this handle three inputs? Probably custom
                # based on class. Test with Struct.
                if hasattr(input_attributes, "left") and hasattr(
                        input_attributes, "right"
                ):
                    # Right Side, i.e. the inputs.
                    left_input_id = input_attributes.right.name
                    right_input_id = input_attributes.left.name
                    left_node = self.get_node_by_node_name(left_input_id)
                    right_node = self.get_node_by_node_name(right_input_id)
                    self.add_edge(left_node, ref_node)
                    self.add_edge(right_node, ref_node)
                    # Left Side, i.e. the outputs.
                    output_id = item.left.var.name
                    out_node = self.get_node_by_node_name(output_id)
                    self.add_edge(ref_node, out_node)
                    # Then we add all of the pointers
                    left_node.output_signal = ref_node
                    right_node.output_signal = ref_node
                    ref_node.input_signals = [left_node, right_node]
                    out_node.input_signals = [ref_node]

    # ---------------------------- LOGIC SIMULATION ----------------------------

    def get_logical_output(
            self,
            input_signals: Union[List[bool], Tuple[bool], Dict[str, bool]],
            output_index: int = 0,
    ) -> bool:
        """
        Get the boolean output of the CircuitNetwork given the passed in
        input signals.

        Args:
            input_signals: The input signals into the circuit. The various
            types are coerced into a uniform approach within the function.

        Returns:
            The logical output given the inputs to the circuit. (True | False)
        """
        available_inputs = self.get_available_inputs()
        if len(input_signals) != len(available_inputs):
            raise RuntimeError(
                f"Requested input signals do not match with available inputs."
                f"Requested input signal: {input_signals}\n"
                f"Available inputs: {available_inputs}\n"
            )
        if type(input_signals) == dict:
            for key in input_signals:
                signal_value = input_signals[key]
                node = self.get_node_by_node_name(key)
                node.boolean_value = signal_value
        else:
            for node, signal_value in zip(
                    self.input_signal_node_list,
                    input_signals,
            ):
                node.boolean_value = signal_value
        # We then run the graph to get the final output.
        # This assumes that we have a singular output. Our approach below is
        # amenable to multiple outputs, but I need to do some additional
        # research before I pursue it.
        output_node = self.output_signal_node_list[output_index]
        res = self.perform_traversal(output_node)
        return res

    def generate_truth_table(self):
        logical_inputs = list(
            itertools.product(
                [True, False],
                repeat=len(self.get_available_inputs())
            )
        )
        # These are implicitly in canonical discrete mathematics ordering for
        # construction of a truth table.
        out_array = np.zeros(
            shape=(
                len(logical_inputs),
                self.get_number_of_inputs() + self.get_number_of_outputs(),
            )
        )
        for logical_input_index, logical_input in enumerate(logical_inputs):
            input_offset = len(logical_input)
            for truth_index, truth_value in enumerate(logical_input):
                out_array[logical_input_index][truth_index] = truth_value
            for logical_output_index in range(self.get_number_of_outputs()):
                res = self.get_logical_output(logical_input, logical_output_index)
                out_array[logical_input_index][input_offset + logical_output_index] = res
        return out_array

    def generate_truth_vector(self, input_array: np.ndarray, output_index: int):
        """

        Args:
            input_array:
            output_index:

        Returns:

        """
        logical_inputs = list(
            itertools.product(
                [True, False],
                repeat=len(self.get_available_inputs())
            )
        )
        input_offset = len(logical_inputs[0])
        return input_array[input_offset + output_index, :].T

    def perform_traversal(
            self,
            root_node: LogicNode,
    ) -> bool:
        """
        Recursive function to parse the outputs of all of the nodes of the
        network. This presumes a fairly rigid tree-like structure at the
        moment, and should be expanded in the future.

        Returns:
            Boolean output of the node being evaluated.

        """
        if root_node.input_signals is not None:
            # You could imagine here that we could just iterate over the number
            # of input signals, but I'm limiting it for the moment.
            if len(root_node.input_signals) == 1:
                progenitor = root_node.input_signals[0]
                # A NOT is evaluated here.
                # if root_node.logical_function is not None:
                #     return root_node.logical_function(
                #         self.perform_traversal(progenitor)
                #     )
                # else:
                return self.perform_traversal(progenitor)
            if len(root_node.input_signals) > 1:
                # We assume that if you have multiple inputs you are something
                # that performs some sort of logic.
                left = root_node.input_signals[0]
                right = root_node.input_signals[1]
                l_out = self.perform_traversal(left)
                r_out = self.perform_traversal(right)
                return root_node.logical_function(l_out, r_out)
        # If we get here, we assume that we're an input node and we
        # just need to return our value.
        else:
            return root_node.boolean_value

    # -------------------------------- UTILITY ---------------------------------
    @staticmethod
    def cleanup():
        """
        Pyverilog is messy and doesn't clean up after itself. This should
        probably be run at the exit of the primary Ibis execution as well.
        """
        cleanup_list = ["parser.out", "parsetab.py"]
        for file in cleanup_list:
            if os.path.isfile(file):
                try:
                    os.remove(file)
                except PermissionError:
                    print("Failed to clear prior verilog parsing remnants.")

    def rank_nodes(self):
        for node_name in self.get_available_outputs():
            node = self.get_node_by_node_name(node_name)
            # All input nodes have a rank of zero.
            node.node_rank = 0
            # Should be unique.

    def plot_graph(
            self,
            x_delta: int = 100,
            y_delta: int = 50,
            save_file: bool = False,
            output_filename: str = f"test.jpg",
    ):
        """
        Plots the network structure. Primarily for troubleshooting and
        validation. We don't enforce a rigid structure here, so the output
        may be confusing to a layperson.

        Args:
            save_file: Whether to save the file or not.
            output_filename: What to save the file as.
        """
        labels = {}
        self.rank_nodes()
        # Then we create an implicit ordering based on these locations
        for node in list(self.graph.nodes):
            labels[node] = node.node_name
        # I kind of like the Kamada graph.
        # pos = nx.kamada_kawai_layout(self.graph)
        plt.figure(num=None, figsize=(15, 15), dpi=80)
        nx.draw(
            self.graph,
            labels=labels,
            pos=nx.nx_agraph.graphviz_layout(self.graph, prog='dot'),
            with_labels=True,
            horizontalalignment='left',
            verticalalignment='bottom',
        )
        if not save_file:
            plt.show()
        else:
            plt.savefig(output_filename)

    def calculate_simple_graph(self):
        pass

    def save_netlist(
            self,
            output_fp: str
    ):
        simple_graph = nx.convert_node_labels_to_integers(self.graph)
        nx.write_edgelist(simple_graph, output_fp, data=False)

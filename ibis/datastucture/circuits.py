"""
--------------------------------------------------------------------------------
Description:
Datastructure describing the various attributes of a Genetic Circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from dataclasses import dataclass, field, asdict
from typing import (
    Dict,
    List,
    Tuple,
)

import matplotlib.pyplot as plt
import networkx as nx

from .parts import BasePart, PART_LUT


@dataclass
class SBOLGeneticGroup:
    name: str
    components: Dict[str, BasePart] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)


@dataclass
class SBOLGeneticCircuit:
    name: str
    groups: Dict[str, SBOLGeneticGroup] = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)


# ----------------------- Network Based Genetic Circuits  ----------------------


class NetworkGeneticNode:
    def __init__(self):
        self.key_name: str = None
        self.part_type: str = None
        self.part_class: BasePart = None
        self.sequence: str = None
        self.ancestor_node: NetworkGeneticNode = None
        self.descendant_node: NetworkGeneticNode = None
        self.bound_node: NetworkGeneticNode = None


class NetworkGeneticCircuit:
    def __init__(self, sbol_input: SBOLGeneticCircuit):
        self.graph = nx.Graph()
        self.node_lut = {}
        self.parse_sbol_input(sbol_input)

    def parse_sbol_input(self, sbol_input: SBOLGeneticCircuit):
        """

        Args:
            sbol_input:

        Returns:

        """
        prior_node = None
        for group in sbol_input.groups:
            components = sbol_input.groups[group].components
            for component in components:
                part = components[component]
                current_node = NetworkGeneticNode()
                current_node.key_name = component
                current_node.part_type = part.get_name()
                current_node.part_class = part
                current_node.sequence = part.dna_sequence
                self.graph.add_node(current_node)
                if prior_node is not None:
                    # TODO: At a future date we should probably count on the
                    # addition of specific edge types, namely ones that
                    # represent a partitioned circuit and ones that represent
                    # relationships between nodes that aren't sequential, e.g.
                    # a repressor and a downstream promoter.
                    current_node.ancestor_node = prior_node
                    self.graph.add_edge(
                        prior_node,
                        current_node,
                        edge_type="linear",
                    )
                prior_node = current_node
                # Make sure that every entry has a unique key.
                component_name = component
                count = 1
                while component_name in self.node_lut.keys():
                    count += 1
                    component_name = f"{component}_{count}"
                self.node_lut[component] = current_node
        # You've iterated over the breadth of the network, and now you need to
        # chain everything backwards for convenience so you can pull out both
        # the parent_node and the child_node in case you need to do any
        # operations or analysis based on localized areas within the network
        # structure.
        # NOTE: This only works for a 1D network structure. If we need to do
        # bifurcated networks in the future we'll have to revisit this.
        if prior_node is not None:
            current_node = prior_node
            while current_node.ancestor_node is not None:
                ancestor = current_node.ancestor_node
                ancestor.descendant_node = current_node
                current_node = ancestor
        # This is sort of bullshit, but the way I've seen people doing this
        # is that the promoter binding works with the names starting with
        # a P. This'll probably have to be revisited, or probably it's better
        # done in a canonical representation of SBOL vice our own probably
        # broken implementation.
        for node_key in self.node_lut:
            if node_key.startswith("p"):
                if node_key[1:] in self.node_lut:
                    bound_key = node_key[1:]
                    self.node_lut[node_key].bound_node = self.node_lut[bound_key]
                    self.node_lut[bound_key].bound_node = self.node_lut[node_key]
                    self.graph.add_edge(
                        self.node_lut[node_key],
                        self.node_lut[bound_key],
                        edge_type="bound",
                    )

    def get_nodes(self) -> List[NetworkGeneticNode]:
        return list(self.graph.nodes)

    def get_nodes_by_part(self, part_name: str) -> List[NetworkGeneticNode]:
        """

        Args:
            part_name:

        Returns:

        """
        # TODO: This string manipulation is silly and I should fix it. - Jx.
        part_name = part_name.lower().capitalize()
        if part_name not in list(map(str.capitalize, list(PART_LUT.keys()))):
            raise RuntimeError(
                f"{part_name} is not a recognized part type. Recognized part "
                f"types are {PART_LUT.keys()}"
            )
        ret_list = []
        for node in self.get_nodes():
            if node.part_type == part_name:
                ret_list.append(node)
        return ret_list

    def get_bound_nodes(self) -> List[Tuple[NetworkGeneticNode]]:
        """

        Returns:

        """
        ret_list = []
        node_iter = self.get_nodes()
        for node in node_iter:
            if node.bound_node is not None:
                ret_list.append(tuple([node, node.bound_node]))
                node_iter.remove(node.bound_node)
        return ret_list

    def filter_graph(self, filter_criteria: str) -> nx.Graph:
        """

        Args:
            filter_criteria:

        Returns:

        """
        filtered_graph = nx.Graph()
        for node_1, node_2, attr_dict in self.graph.edges(data=True):
            if attr_dict["edge_type"] == filter_criteria:
                filtered_graph.add_node(node_1)
                filtered_graph.add_node(node_2)
                filtered_graph.add_edge(node_1, node_2, **attr_dict)
        return filtered_graph

    def plot_graph(
        self,
        save_file: bool = False,
        output_filename: str = f"test.jpg",
        filtered_graph: nx.Graph = None,
    ):
        """

        Args:
            save_file:
            output_filename:
            filtered_graph:

        Returns:

        """
        graph = filtered_graph if filtered_graph is not None else self.graph
        labels = {}
        for node in list(graph.nodes):
            labels[node] = node.key_name
        nx.draw(graph, labels=labels, with_labels=True)
        if not save_file:
            plt.show()
        else:
            plt.savefig(output_filename)

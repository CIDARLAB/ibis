"""
--------------------------------------------------------------------------------
Description:
Datastructure describing the various attributes of a Genetic Circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from dataclasses import dataclass, field
from typing import (
    Dict,
)

import networkx as nx

from .parts import BasePart


@dataclass
class SBOLGeneticGroup:
    name: str
    components: Dict[str, BasePart] = field(default_factory=dict)


@dataclass
class SBOLGeneticCircuit:
    name: str
    groups: Dict[str, SBOLGeneticGroup] = field(default_factory=dict)


# ----------------------- Network Based Genetic Circuits  ----------------------
class NetworkGeneticCircuit:
    pass

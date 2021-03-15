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

from .parts import BasePart


@dataclass
class GeneticGroup:
    name: str
    components: Dict[str, BasePart] = field(default_factory=dict)


@dataclass
class GeneticCircuit:
    name: str
    groups: Dict[str, GeneticGroup] = field(default_factory=dict)

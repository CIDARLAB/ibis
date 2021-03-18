"""
--------------------------------------------------------------------------------
Description:
Datastructure describing a part of a genetic circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from dataclasses import dataclass


# TODO: I should probably add the ABC stuff here to be uniform in approach. -Jx


@dataclass
class BasePart:
    dna_sequence: str = None

    def get_name(self):
        return type(self).__name__


@dataclass
class Promoter(BasePart):
    pass


@dataclass
class RibosomeEntrySite(BasePart):
    pass


@dataclass
class CodingSequence(BasePart):
    pass


@dataclass
class Terminator(BasePart):
    pass


@dataclass
class RibonucleaseSite(BasePart):
    pass


@dataclass
class EngineeredRegion(BasePart):
    pass


PART_LUT = {
    "promoter": Promoter,
    "ribosome_entry_site": RibosomeEntrySite,
    "coding_sequence": CodingSequence,
    "terminator": Terminator,
    "ribosome_nuclease_site": RibonucleaseSite,
    "engineered_region": EngineeredRegion,
}


def get_part_object_from_str(part_type: str):
    part_type = part_type.lower()
    return PART_LUT[part_type]

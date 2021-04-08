"""
--------------------------------------------------------------------------------
Description:
Ingress of SBOL XML File into internal genetic circuit datastructure

Notes:
    The test cases being currently used are generated from CelloV2, so be wary
    of it being actually correct given past performance.

    TODO: Ask Doug or Myers for some formal 'official' SBOL XML that
    composes the entirety of a Genetic Circuit to ensure compliance with
    standard.

    TODO: I don't get how they represent the relationship (called 'arcs' in some
    of the other literature) between a repressor/inducer and some other element
    in the XML. I probably need to do some reading in the standard.

References:
    SBOL Standard Visuals: https://sbolstandard.org/visual-glyphs/

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import os
import xml.etree.ElementTree as ET

from ibis.datastucture import (
    SBOLGeneticGroup,
    SBOLGeneticCircuit,
    get_part_object_from_str,
)

SBOL_PREFIX = "{http://sbols.org/v2#}"
W3_KEY = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
ABOUT_KEY = f"{W3_KEY}about"
RESOURCE_KEY = f"{W3_KEY}resource"


def get_part_position(reference: str, root_node: ET.Element) -> int:
    """
    Finds the starting position of the part.

    Args:
        reference: Persistent text reference key that ties SBOL Components to
            SBOL Sequence Annotation
        root_node: The root node of the XML tree. Needed information is on
            separate 'branches', so you need to iterate over the root.

    Returns:
        The starting position of the requested part.

    """
    sequences = root_node.findall(f"{SBOL_PREFIX}sequenceAnnotation")
    for sequence in sequences:
        seq = sequence.find(f"{SBOL_PREFIX}SequenceAnnotation")
        if seq.find(f"{SBOL_PREFIX}component").attrib[RESOURCE_KEY] == reference:
            loc = seq.find(f"{SBOL_PREFIX}location")
            range = loc.find(f"{SBOL_PREFIX}Range")
            start = int(range.find(f"{SBOL_PREFIX}start").text)
            return start
    # If we got here, we could not find it so we can't order our input genetic
    # circuit. We then bail as there is no recourse.
    raise RuntimeError("Unable to locate genetic part in sequence.")


def get_part_name(reference: str) -> str:
    """
    Extracts the part name from a passed in SBOL Component reference.

    Args:
        reference: Input string. Should look something like
        <https://synbiohub.programmingbiology.org/user/wrjackso/test/
        Design0_Group1_Object2/pTet_Component/1>

    Returns:
        Base Component Name. With above example, would be 'pTet'

    """
    return reference.split("/")[-2].split("_Component")[0]


def get_part_type(part_name: str, root_node: ET.Element) -> str:
    """
    Gets the part type.

    Args:
        part_name: The base name of the part, e.g, 'yfp_cassette'
        root_node: The root node of the XML tree.

    Returns:
        The string name of the part. Reference `datastructures/parts` for
        ensuring 1:1 mapping between strings and classes.
    """
    identifiers_lut = {
        "0000167": "promoter",
        "0001977": "ribosome_nuclease_site",
        "0000141": "terminator",
        "0000316": "coding_sequence",
        "0000139": "ribosome_entry_site",
        "0000804": "engineered_region",
    }
    components = root_node.findall(f"{SBOL_PREFIX}ComponentDefinition")
    for component in components:
        if component.find(f"{SBOL_PREFIX}displayId").text == part_name:
            part_ref = component.find(f"{SBOL_PREFIX}role")
            identifier = part_ref.attrib[RESOURCE_KEY].split(":")[-1]
            try:
                return identifiers_lut[identifier]
            except KeyError:
                raise KeyError(f"Part {part_name} not recognized.")
    raise RuntimeError(f"Unable to identify part number for {part_name}")


def get_sequence_string(part_name: str, root_node: ET.Element) -> str:
    """
    Gets the genetic sequence associated with the passed in part name.

    TODO: We might need it? Unsure. -Jx.

    Args:
        part_name: The base name of the part, e.g, 'yfp_cassette'
        root_node: The root node of the XML tree.

    Returns:
        GCAT representation of the sequence.

    """
    sequence_name = part_name + "_sequence"
    sequences = root_node.findall(f"{SBOL_PREFIX}Sequence")
    for sequence in sequences:
        if sequence.find(f"{SBOL_PREFIX}displayId").text == sequence_name:
            seq_text = sequence.find(f"{SBOL_PREFIX}elements").text
            return seq_text


def parse_sbol_xml_tree(fp: str) -> SBOLGeneticCircuit:
    """
    Parses an XML file and returns a `GeneticCircuit` Datastructure.

    Args:
        fp: The filepath to the circuit.

    Returns:
        `GeneticCircuit` Datastructure.

    """
    # We probably shouldn't put a guard or catch around this because file not
    # found should be self explanatory
    tree = ET.parse(fp)
    root = tree.getroot()
    # Some sort of validation goes here to ensure compliance with standard.
    # Currently this is using Cello output as the standard, beware.
    circuit_name = os.path.splitext(os.path.basename(fp))[0]
    genetic_circuit = SBOLGeneticCircuit(name=circuit_name)
    design_groups = []
    for item in root.findall(f"{SBOL_PREFIX}ComponentDefinition"):
        display_name = item.find(f"{SBOL_PREFIX}displayId").text
        if "Object" in display_name:
            design_groups.append(item)
    for group in design_groups:
        group_name = group.find(f"{SBOL_PREFIX}displayId").text
        genetic_group = SBOLGeneticGroup(group_name)
        raw_parts = []
        object_node = group
        # The following loops are just to order the parts and pull out relevant
        # data for datastructure generation, as they don't seem to be implicitly
        # ordered.
        for component in object_node.findall(f"{SBOL_PREFIX}component"):
            raw_parts.append(component)
        unsorted_parts = []
        for part in raw_parts:
            # Yes, it's double-nested and only delineated by a change in
            # capitalization.  ¯\_(ツ)_/¯
            component = part.find(f"{SBOL_PREFIX}Component")
            reference = component.attrib[ABOUT_KEY]
            part_name = get_part_name(reference)
            part_type = get_part_type(part_name, root)
            dna_sequence = get_sequence_string(part_name, root)
            part_position = get_part_position(reference, object_node)
            unsorted_parts.append(
                tuple([part, part_position, part_name, part_type, dna_sequence])
            )
        sorted_parts = sorted(unsorted_parts, key=lambda x: x[1])
        for part in sorted_parts:
            part, _, part_name, part_type, dna_sequence = part
            part_class = get_part_object_from_str(part_type)
            part_obj = part_class(dna_sequence=dna_sequence)
            genetic_group.components[part_name] = part_obj
        genetic_circuit.groups[group_name] = genetic_group
    return genetic_circuit


if __name__ == "__main__":
    input_file = "../../tests/test_cello/example_and_gate.xml"
    gc = parse_sbol_xml_tree(input_file)
    print(gc)

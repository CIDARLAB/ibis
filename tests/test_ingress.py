"""
--------------------------------------------------------------------------------
Description:
Tests for the Ingress Module

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from ibis.ingress import parse_sbol_xml_tree


def test_ingress_module():
    input_file = "tests/test_circuits/example_and_gate.xml"
    gc = parse_sbol_xml_tree(input_file)
    print(gc)

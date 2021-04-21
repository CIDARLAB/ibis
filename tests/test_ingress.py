"""
--------------------------------------------------------------------------------
Description:
Tests for the Ingress Module

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import pathlib

import pytest

from ibis.ingress import parse_sbol_xml_tree
from ibis.datastucture import (
    NetworkGeneticCircuit,
    NetworkGeneticNode,
    parse_cello_input_file,
)

example_input_dict = {
    "name": "example_and_gate",
    "groups": {
        "Design0_Group1_Object0": {
            "name": "Design0_Group1_Object0",
            "components": {
                "pSrpR": {
                    "dna_sequence": "TCTATGATTGGTCCAGATTCGTTACCAATTGACAGCTAGCTC"
                    "AGTCCTAGGTATATACATACATGCTTGTTTGTTTGTAAAC"
                },
                "pHlyIIR": {
                    "dna_sequence": "ACCAGGAATCTGAACGATTCGTTACCAATTGACATATTTAAAA"
                    "TTCTTGTTTAAAatgctagc"
                },
                "RiboJ53": {
                    "dna_sequence": "CTGAAGCGGTCAACGCATGTGCTTTGCGTTCTGATGAGACAGT"
                    "GATGTCGAAACCGCCTCTACAAATAATTTTGTTTAA"
                },
                "P2": {"dna_sequence": "GGAGCTATGGACTATGTTTGAAAGGCTGAAATACTAG"},
                "PhlF": {
                    "dna_sequence": "ATGGCACGTACCCCGAGCCGTAGCAGCATTGGTAGCCTGCGTA"
                    "GTCCGCATACCCATAAAGCAATTCTGACCAGCACCATTGAAAT"
                    "CCTGAAAGAATGTGGTTATAGCGGTCTGAGCATTGAAAGCGTT"
                    "GCACGTCGTGCCGGTGCAAGCAAACCGACCATTTATCGTTGGT"
                    "GGACCAATAAAGCAGCACTGATTGCCGAAGTGTATGAAAATGA"
                    "AAGCGAACAGGTGCGTAAATTTCCGGATCTGGGTAGCTTTAAA"
                    "GCCGATCTGGATTTTCTGCTGCGTAATCTGTGGAAAGTTTGGC"
                    "GTGAAACCATTTGTGGTGAAGCATTTCGTTGTGTTATTGCAGA"
                    "AGCACAGCTGGACCCTGCAACCCTGACCCAGCTGAAAGATCAG"
                    "TTTATGGAACGTCGTCGTGAGATGCCGAAAAAACTGGTTGAAA"
                    "ATGCCATTAGCAATGGTGAACTGCCGAAAGATACCAATCGTGA"
                    "ACTGCTGCTGGATATGATTTTTGGTTTTTGTTGGTATCGCCTG"
                    "CTGACCGAACAGCTGACCGTTGAACAGGATATTGAAGAATTTA"
                    "CCTTCCTGCTGATTAATGGTGTTTGTCCGGGTACACAGCGTTA"
                    "A"
                },
                "ECK120033737": {
                    "dna_sequence": "GGAAACACAGAAAAAAGCCCGCACCTGACAGTGCGGGCTTTTT"
                    "TTTTCGACCAAAGG"
                },
            },
        },
        "Design0_Group1_Object1": {
            "name": "Design0_Group1_Object1",
            "components": {
                "pTac": {
                    "dna_sequence": "AACGATCGTTGGCTGTGTTGACAATTAATCATCGGCTCGTATA"
                    "ATGTGTGGAATTGTGAGCGCTCACAATT"
                },
                "RiboJ10": {
                    "dna_sequence": "CTGAAGCGCTCAACGGGTGTGCTTCCCGTTCTGATGAGTCCGT"
                    "GAGGACGAAAGCGCCTCTACAAATAATTTTGTTTAA"
                },
                "S2": {"dna_sequence": "GAGTCTATGGACTATGTTTTCACATATGAGATACCAGG"},
                "SrpR": {
                    "dna_sequence": "ATGGCACGTAAAACCGCAGCAGAAGCAGAAGAAACCCGTCAGC"
                    "GTATTATTGATGCAGCACTGGAAGTTTTTGTTGCACAGGGTGT"
                    "TAGTGATGCAACCCTGGATCAGATTGCACGTAAAGCCGGTGTT"
                    "ACCCGTGGTGCAGTTTATTGGCATTTTAATGGTAAACTGGAAGT"
                    "TCTGCAGGCAGTTCTGGCAAGCCGTCAGCATCCGCTGGAACTG"
                    "GATTTTACACCGGATCTGGGTATTGAACGTAGCTGGGAAGCAG"
                    "TTGTTGTTGCAATGCTGGATGCAGTTCATAGTCCGCAGAGCAA"
                    "ACAGTTTAGCGAAATTCTGATTTATCAGGGTCTGGATGAAAGC"
                    "GGTCTGATTCATAATCGTATGGTTCAGGCAAGCGATCGTTTTC"
                    "TGCAGTATATTCATCAGGTTCTGCGTCATGCAGTTACCCAGGG"
                    "TGAACTGCCGATTAATCTGGATCTGCAGACCAGCATTGGTGTT"
                    "TTTAAAGGTCTGATTACCGGTCTGCTGTATGAAGGTCTGCGTA"
                    "GCAAAGATCAGCAGGCACAGATTATCAAAGTTGCACTGGGTAG"
                    "CTTTTGGGCACTGCTGCGTGAACCGCCTCGTTTTCTGCTGTGT"
                    "GAAGAAGCACAGATTAAACAGGTGAAATCCTTCGAATAA"
                },
                "ECK120029600": {
                    "dna_sequence": "TTCAGCCAAAAAACTTAAGACCGCCGGTCTTGTCCACTACCTT"
                    "GCAGTAATGCGGTGGACAGGATCGGCGGTTTTCTTTTCTCTTC"
                    "TCAA"
                },
            },
        },
        "Design0_Group1_Object2": {
            "name": "Design0_Group1_Object2",
            "components": {
                "pTet": {
                    "dna_sequence": "TACTCCACCGTTGGCTTTTTTCCCTATCAGTGATAGAGATTGA"
                    "CATCCCTATCAGTGATAGAGATAATGAGCAC"
                },
                "RiboJ51": {
                    "dna_sequence": "CTGAAGTAGTCACCGGCTGTGCTTGCCGGTCTGATGAGCCTGT"
                    "GAAGGCGAAACTACCTCTACAAATAATTTTGTTTAA"
                },
                "H1": {"dna_sequence": "ACCCCCGAG"},
                "HlyIIR": {
                    "dna_sequence": "ATGAAATACATCCTGTTTGAGGTGTGCGAAATGGGTAAAAGCC"
                    "GTGAACAGACCATGGAAAATATTCTGAAAGCAGCCAAAAAGAA"
                    "ATTCGGCGAACGTGGTTATGAAGGCACCAGCATTCAAGAAATT"
                    "ACCAAAGAAGCCAAAGTTAACGTTGCAATGGCCAGCTATTACT"
                    "TTAATGGCAAAGAGAACCTGTACTACGAGGTGTTCAAAAAATA"
                    "CGGTCTGGCAAATGAACTGCCGAACTTTCTGGAAAAAAACCAG"
                    "TTTAATCCGATTAATGCCCTGCGTGAATATCTGACCGTTTTTA"
                    "CCACCCACATTAAAGAAAATCCGGAAATTGGCACCCTGGCCTA"
                    "TGAAGAAATTATCAAAGAAAGCGCACGCCTGGAAAAAATCAAA"
                    "CCGTATTTTATCGGCAGCTTCGAACAGCTGAAAGAAATTCTGC"
                    "AAGAGGGTGAAAAACAGGGTGTGTTTCACTTTTTTAGCATCAA"
                    "CCATACCATCCATTGGATTACCAGCATTGTTCTGTTTCCGAAA"
                    "TTCAAAAAATTCATCGATAGCCTGGGTCCGAATGAAACCAATG"
                    "ATACCAATCATGAATGGATGCCGGAAGATCTGGTTAGCCGTAT"
                    "TATTAGCGCACTGACCGATAAACCGAACATTTAA"
                },
                "ECK120033736": {
                    "dna_sequence": "aacgcatgagAAAGCCCCCGGAAGATCACCTTCCGGGGGCTTT"
                    "tttattgcgc"
                },
            },
        },
        "Design0_Group2_Object0": {
            "name": "Design0_Group2_Object0",
            "components": {
                "pPhlF": {
                    "dna_sequence": "CGACGTACGGTGGAATCTGATTCGTTACCAATTGACATGATAC"
                    "GAAACGTACCGTATCGTTAAGGT"
                },
                "YFP_cassette": {
                    "dna_sequence": "CTGAAGCTGTCACCGGATGTGCTTTCCGGTCTGATGAGTCCGT"
                    "GAGGACGAAACAGCCTCTACAAATAATTTTGTTTAATACTAGA"
                    "GAAAGAGGGGAAATACTAGATGGTGAGCAAGGGCGAGGAGCTG"
                    "TTCACCGGGGTGGTGCCCATCCTGGTCGAGCTGGACGGCGACG"
                    "TAAACGGCCACAAGTTCAGCGTGTCCGGCGAGGGCGAGGGCGA"
                    "TGCCACCTACGGCAAGCTGACCCTGAAGTTCATCTGCACCACA"
                    "GGCAAGCTGCCCGTGCCCTGGCCCACCCTCGTGACCACCTTCG"
                    "GCTACGGCCTGCAATGCTTCGCCCGCTACCCCGACCACATGAA"
                    "GCTGCACGACTTCTTCAAGTCCGCCATGCCCGAAGGCTACGTC"
                    "CAGGAGCGCACCATCTTCTTCAAGGACGACGGCAACTACAAGA"
                    "CCCGCGCCGAGGTGAAGTTCGAGGGCGACACCCTGGTGAACCG"
                    "CATCGAGCTGAAGGGCATCGACTTCAAGGAGGACGGCAACATC"
                    "CTGGGGCACAAGCTGGAGTACAACTACAACAGCCACAACGTCT"
                    "ATATCATGGCCGACAAGCAGAAGAACGGCATCAAGGTGAACTT"
                    "CAAGATCCGCCACAACATCGAGGACGGCAGCGTGCAGCTCGCC"
                    "GACCACTACCAGCAGAACACCCCAATCGGCGACGGCCCCGTGC"
                    "TGCTGCCCGACAACCACTACCTTAGCTACCAGTCCGCCCTGAG"
                    "CAAAGACCCCAACGAGAAGCGCGATCACATGGTCCTGCTGGAG"
                    "TTCGTGACCGCCGCCGGGATCACTCTCGGCATGGACGAGCTGT"
                    "ACAAGTAACTCGGTACCAAATTCCAGAAAAGAGGCCTCCCGAA"
                    "AGGGGGGCCTTTTTTCGTTTTGGTCC"
                },
            },
        },
    },
}


@pytest.fixture
def get_input_and_gate():
    current_dir = pathlib.Path.cwd().parts[-1]
    # Assumes that you are running this file for testing.
    if current_dir == "tests":
        input_file = "test_cello/example_and_gate.xml"
    else:
        # Assumes you are running this at the top level.
        input_file = "tests/test_cello/example_and_gate.xml"
    return input_file

@pytest.fixture
def get_input_sensor_ucf():
    current_dir = pathlib.Path.cwd().parts[-1]
    # Assumes that you are running this file for testing.
    if current_dir == "tests":
        input_file = "test_cello/test_ucf_files/Eco1C1G1T1.input.json"
    else:
        # Assumes you are running this at the top level.
        input_file = "tests/test_cello/test_ucf_files/Eco1C1G1T1.input.json"
    return input_file


def test_ingress_module(get_input_and_gate):
    input_file = get_input_and_gate
    gc = parse_sbol_xml_tree(input_file)
    gc_dict = gc.as_dict()
    assert gc_dict == example_input_dict


def test_graph_construction(get_input_and_gate):
    input_file = get_input_and_gate
    gc = parse_sbol_xml_tree(input_file)
    gn = NetworkGeneticCircuit(sbol_input=gc)
    promoter_parts = gn.get_nodes_by_part("Promoter")
    assert len(promoter_parts) == 5
    bound_nodes = gn.get_bound_nodes()
    assert len(bound_nodes) == 3


def test_graph_filtration(get_input_and_gate):
    input_file = get_input_and_gate
    gc = parse_sbol_xml_tree(input_file)
    gn = NetworkGeneticCircuit(sbol_input=gc)
    ogn = gn.filter_graph("bound")
    assert len(ogn) == 6  # 3 sets of 2 elements = 6
    # All nodes in the primary graph have a regular edge
    assert len(gn.get_nodes()) == 18
    # Not useful in an automated testing framework, but if you wanna know what
    # it looks like.
    # gn.plot_graph(filtered_graph=ogn)

def test_ucf_parsing(get_input_sensor_ucf):
    input_file = get_input_sensor_ucf
    parsed_input = parse_cello_input_file(input_file)
    tetr = parsed_input.get_sensor('TetR_sensor')
    assert round(tetr.get_score(1)) == 4



if __name__ == "__main__":
    # test_ingress_module(get_input_and_gate())
    test_graph_construction(get_input_and_gate())
    test_graph_filtration(get_input_and_gate())

"""
--------------------------------------------------------------------------------
Description:
Tests our ability to parse verilog and come to the correct logical conclusions.

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import itertools
import os
import pathlib

import pytest
import networkx as nx
import matplotlib.pyplot as plt
from ibis.datastucture.logic import LogicNetwork


# @pytest.fixture
def get_test_verilog_directory():
    current_dir = pathlib.Path.cwd().parts[-1]
    # Assumes that you are running this file for testing.
    if current_dir == "tests":
        return os.path.join("test_verilog")
    return os.path.join("tests", "test_verilog")


def test_and_gate():
    path = get_test_verilog_directory()
    file_location = os.path.join(path, "and.v")
    # Exercise the truth table. Trivial I know. Simple AND Table, 2 Inputs 1 Out
    c_net = LogicNetwork(verilog_fp=file_location)
    assert c_net.get_logical_output([False, False]) is False
    assert c_net.get_logical_output([True, False]) is False
    assert c_net.get_logical_output([False, True]) is False
    assert c_net.get_logical_output([True, True]) is True


def test_and_expansion():
    path = get_test_verilog_directory()
    file_location = os.path.join(path, "and.v")
    # Exercise the truth table. Trivial I know. Simple AND Table, 2 Inputs 1 Out
    c_net = LogicNetwork(verilog_fp=file_location)
    c_net.perform_nor_logic_expansion()
    c_net.plot_graph()

def test_or_gate():
    path = get_test_verilog_directory()
    file_location = os.path.join(path, "or.v")
    # Exercise the truth table. Trivial I know. Simple AND Table, 2 Inputs 1 Out
    c_net = LogicNetwork(verilog_fp=file_location)
    assert c_net.get_logical_output([False, False]) is False
    assert c_net.get_logical_output([True, False]) is True
    assert c_net.get_logical_output([False, True]) is True
    assert c_net.get_logical_output([True, True]) is True


def test_struct():
    path = get_test_verilog_directory()
    file_location = os.path.join(path, "struct.v")
    c_net = LogicNetwork(verilog_fp=file_location)
    thing = c_net.get_logical_output([True, True, True])


def test_sr_latch():
    # TODO: When we start doing circuits with loops.
    pass


if __name__ == '__main__':
    test_and_expansion()
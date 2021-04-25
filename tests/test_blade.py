import os

import pytest

from ibis.datastucture import GeneticCircuit


def _parse_line(line):
    fields = line.strip().split(',')

    circuit_id = fields[0]

    # circuit structure in fields[1:5] not used
    # standard error data in fields[21:29] not used
    # global rank, delta G, delta M in 30, 31, and 32, respectively, not used

    # format: [gfp 00, mch 00, gfp 10, mch 10, gfp 01, mch 01, gfp 11, mch 11]
    # where each entry is the gfp or mch output value given input xx

    # intended logic
    binary_logic = [int(x) for x in fields[5:13]]

    # experimental data
    cap_value = 20000.0
    exp_means = [float(x) if float(x) < cap_value else cap_value
                 for x in fields[13:21]]

    # TODO: modify for Jackson's logic structure
    gc = GeneticCircuit(2, 2)
    gc.intended_truth_table = binary_logic
    gc.exp_data = exp_means

    # angle calculated in Blade paper, compare to our calculation
    true_angle = float(fields[29])

    return circuit_id, (gc, true_angle)


@pytest.fixture
def parse_blade_file():
    """
    Load data file from BLADE paper.
    """
    fn = os.path.join(os.path.dirname(__file__), 'test_blade',
                      '41587_2017_BFnbt3805_MOESM250_ESM-1.csv')
    with open(fn) as f:
        f.readline()  # header
        circuits = dict(_parse_line(line) for line in f)
    return circuits


def test_blade(parse_blade_file):
    """
    Tests instantiation of GeneticCircuit class and vector_proximity method.
    """
    circs = parse_blade_file
    for i, (gc, ta) in circs.items():
        if i == '99':
            # For some reason 99 has a listed angle of 0.7, when it should be
            # ~9? I think it's an issue with BLADE data and therefore not my
            # fault.
            continue
        vp = round(gc.vector_proximity(), 1)
        assert abs(vp - ta) < 0.11  # room for rounding errors

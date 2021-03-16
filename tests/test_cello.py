"""
tests.test_repressor

TODO: WORDS GOOD PLEASE.

W.R. Jackson 2020
"""

import pytest

from ibis.datastucture import (
    InputSignal,
)
from ibis.scoring.cello_score import (
    CelloRepressor,
)

# -------------------------------- Test Fixtures -------------------------------
@pytest.fixture
def generate_s1_gate():
    """
    Generates an S1 Repressor as detailed in assignment.

    Reference Plasmid:
        https://www.addgene.org/74691/
    """
    return CelloRepressor(
        y_max=1.3,
        y_min=0.003,
        k=0.01,
        n=2.9,
        number_of_inputs=1,
    )


@pytest.fixture
def generate_p1_gate():
    """
    Generates an S1 Repressor as detailed in assignment.

    Reference Plasmid:
        https://www.addgene.org/74685/
    """
    return CelloRepressor(
        y_max=3.9,
        y_min=0.01,
        k=0.03,
        n=4,
        number_of_inputs=2,
    )


@pytest.fixture
def generate_plux_star():
    """
    Generates a pLuxStar Biological Input as detailed in the assignment.
    """
    lux = InputSignal(
        label="pLuxStar",
        off_value=0.025,
        on_value=0.31,
    )
    lux.set_binary_value(0b0011)
    return lux


@pytest.fixture
def generate_ptet():
    """
    Generates a pTet Biological Input as detailed in the assignment.
    """
    ptet = InputSignal(
        label="pTet",
        off_value=0.0013,
        on_value=4.4,
    )
    ptet.set_binary_value(0b0101)
    return ptet


# ----------------------------- Datastructure Tests ----------------------------
def test_gate_instantiation(generate_s1_gate):
    """
    Simply tests our ability to generate a gate
    """
    s1 = generate_s1_gate
    assert s1 is not None


def test_input_signal_instantiation(generate_plux_star):
    """
    Simply tests our ability to generate a gate
    """
    plux = generate_plux_star
    assert plux is not None


# -------------------------------- Logic Testing -------------------------------
def test_logic_gate_setting(generate_s1_gate):
    """
    Tests our ability to set a logic gate and correctly generate a logic output.
    """
    s1 = generate_s1_gate
    s1.set_logical_function("NOT")
    s1.set_logical_inputs([0b0101])
    assert s1.get_logical_output() == 0b1010


def test_logic_functions(generate_s1_gate):
    """
    Tests all logical outputs.

    After reading more of the primary literature I'm a little confused on the
    NAND/NOR specification in the assignment when the core paper seems to
    reference almost all logic operations. Maybe an attempt to limit the
    problem?
    """
    s1 = generate_s1_gate
    # Singular input testing.
    s1.set_logical_inputs([0b0101])
    s1.set_logical_function("NOT")
    assert s1.get_logical_output() == 0b1010
    # Multiple input testing
    s1.set_logical_function("AND")
    s1.set_logical_inputs([0b0000, 0b1111])
    assert s1.get_logical_output() == 0b0000

    s1.set_logical_function("OR")
    s1.set_logical_inputs([0b0000, 0b1111])
    assert s1.get_logical_output() == 0b1111

    s1.set_logical_function("XOR")
    s1.set_logical_inputs([0b1010, 0b0101])
    assert s1.get_logical_output() == 0b1111

    s1.set_logical_function("NAND")
    s1.set_logical_inputs([0b1100, 0b0011])
    assert s1.get_logical_output() == 0b1111

    s1.set_logical_function("NOR")
    s1.set_logical_inputs([0b1100, 0b0011])
    assert s1.get_logical_output() == 0b0000

    s1.set_logical_function("XNOR")
    s1.set_logical_inputs([0b1010, 0b1010])
    assert s1.get_logical_output() == 0b1111


# ---------------------------- Repressor Evaluation ----------------------------
def test_response_function_calculation(generate_s1_gate, generate_ptet):
    """
    Tests our ability to calculate response functions for repressors. Tests
    both high and low inputs.
    """
    s1 = generate_s1_gate
    ptet = generate_ptet
    s1.set_biological_inputs([ptet])
    s1.set_logical_function("NOT")
    s1.set_logical_inputs([0b0101])
    # Should be a high signal on output on gate.
    assert s1.calculate_response_function() == pytest.approx(0.0030, 0.1)
    # Now we validate a low signal.
    s1.set_logical_inputs([0b1111])
    assert s1.calculate_response_function() == pytest.approx(1.2965, 0.1)


def test_connected_gates(
    generate_s1_gate,
    generate_p1_gate,
    generate_ptet,
    generate_plux_star,
):
    """
    Tests our ability to connect repressor gates.

    This is the canonical example from page 14.
    """
    s1 = generate_s1_gate
    ptet = generate_ptet
    s1.set_biological_inputs([ptet])
    s1.set_logical_function("NOT")
    s1.set_logical_inputs([0b0101])
    assert s1.calculate_response_function() == pytest.approx(0.0030, 0.1)

    p1 = generate_p1_gate
    plux = generate_plux_star
    p1.set_biological_inputs([plux, s1])
    p1.set_logical_inputs([0b0011, s1])
    p1.set_logical_function("NOR")
    assert p1.get_logical_output() == 0b100
    # Both signals are high in this example
    assert p1.calculate_response_function() == pytest.approx(0.0103, 0.1)

    # Just for the purpose of completeness...
    # S1 Low, Plux High
    s1.set_logical_inputs([0b1111])
    assert p1.calculate_response_function() == pytest.approx(0.0100, 0.1)

    # S1 Low, Plux Low
    p1.set_logical_inputs([0b1111, s1])
    assert p1.calculate_response_function() == pytest.approx(0.0100, 0.1)

    # S1 High, P1 Low
    s1.set_logical_inputs([0b0101])
    assert p1.calculate_response_function() == pytest.approx(2.221, 0.1)


def test_circuit_score(
    generate_s1_gate,
    generate_p1_gate,
    generate_plux_star,
    generate_ptet,
):
    s1 = generate_s1_gate
    ptet = generate_ptet
    s1.set_biological_inputs([ptet])
    s1.set_logical_function("NOT")
    p1 = generate_p1_gate
    plux = generate_plux_star
    p1.set_biological_inputs([plux, s1])
    p1.set_logical_function("NOR")
    assert p1.score_self() == pytest.approx(2.3326, 0.1)


def test_optimize_repressor(
    generate_s1_gate,
    generate_p1_gate,
    generate_plux_star,
    generate_ptet,
):
    s1 = generate_s1_gate
    ptet = generate_ptet
    s1.set_biological_inputs([ptet])
    s1.set_logical_function("NOT")
    results = optimize_repressor(s1, "Nelder-Mead")
    assert results.x[0] == pytest.approx(0.197, 0.1)
    assert results.x[1] == pytest.approx(2.65, 0.1)
    p1 = generate_p1_gate
    plux = generate_plux_star
    p1.set_biological_inputs([plux, s1])
    p1.set_logical_function("NOR")
    results = optimize_repressor(p1, "Nelder-Mead")

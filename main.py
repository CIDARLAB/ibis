"""
--------------------------------------------------------------------------------
Description:
Primary Entrypoint into Ibis

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import os
from pathlib import Path
from typing import (
    List,
    Optional,
)

import pkg_resources
import typer
from rich.console import Console

from ibis.datastucture import (
    NetworkGeneticCircuit,
    LogicNetwork,
)

from ibis.ingress import parse_sbol_xml_tree
from ibis.scoring import (
    get_requirement_map,
    get_scorer_map,
    get_scorer_description,
    generate_template_yaml,
    get_available_scorers,
    validate_input_file,
    generate_requirement_classes,
)
from ibis.utility import (
    plot_cell_edgelist,
)

console = Console()
app = typer.Typer()


# ----------------------- Command Line Utility Functions -----------------------


def name_callback(value: str) -> str:
    """
    Checks whether the first input argument is a valid solver.
    """
    score_map = get_requirement_map()
    if value.lower() not in score_map.keys():
        raise typer.BadParameter("Solver not identified")
    return value


def solver_details_callback(value: bool):
    """
    Provides a brief description of each solver.
    """
    if value:
        typer.secho("Available Solvers...", fg=typer.colors.GREEN)
        for line in get_scorer_description():
            typer.echo(f"{line}")
        raise typer.Exit()


def version_callback(value: bool):
    """
    Returns version of scoring-project when the --version or -v options are called.
    """
    current_ver = pkg_resources.get_distribution("genetic-ibis").version
    if value:
        typer.echo(f"CLI Version: {current_ver}")
        raise typer.Exit()


def complete_name(incomplete: str):
    score_map = get_requirement_map()
    for name, help_text in score_map:
        if name.startswith(incomplete):
            yield name, help_text


# ---------------------------- Application Commands ----------------------------
@app.command()
def generate_template(
        requested_solvers: Optional[List[str]] = typer.Option(None),
        output_fn: Optional[str] = "input.yml",
):
    """
    Generates a template input file for the requested solvers.
    """
    if requested_solvers is not None:
        typer.echo(f"Generating template yaml file for all available solvers...")
    else:
        typer.echo(f"Generating template yaml file for the following solvers:")
        for solver in requested_solvers:
            typer.echo(
                f" - {solver}",
            )
    generate_template_yaml(
        requested_scorers=requested_solvers,
        output_fn=output_fn,
    )
    typer.echo(f"Template File {output_fn} written to {os.getcwd()}")


@app.command()
def score(
        requested_solvers: List[str] = typer.Argument(
            ...,
            help="The Input Solvers",
        ),
        sbol_filepath: str = typer.Option(
            os.path.join(os.getcwd(), "tests", "test_cello", "example_and_gate.xml"),
            help="Filepath: location of the SBOL file that constitutes the genetic "
                 "circuit",
        ),
        parameter_filepath: str = typer.Option(
            os.path.join(os.getcwd(), "input.yml"),
            help="Filepath: location of the SBOL file that constitutes the genetic "
                 "circuit",
        ),
        out_filepath: str = typer.Option(
            "output", help="Filepath: location to write the output of the solved function"
        ),
):
    """
    Takes an SBOL file, evaluates the quality of a genetic circuit, and then outputs performance metrics.
    """
    # We take in our input values and normalize them.
    requested_solvers = [solver.lower() for solver in requested_solvers]
    available_solvers = get_available_scorers()
    for solver in requested_solvers:
        if solver not in available_solvers:
            raise RuntimeError(
                f"Unable to find a scorer with the name {solver}, please "
                f"investigate."
            )
    # We then ensure that our filepaths are correct so we're not breaking down
    # the line.
    if not os.path.isfile(parameter_filepath):
        raise RuntimeError(
            f"Unable to locate input file {parameter_filepath}. Please Investigate."
        )
    # We assume that we'll have multiple forms of output, so what we're doing is
    # validating the output is just an extant directory. If not, we try to
    # generate one.
    if not os.path.isdir(out_filepath):
        os.mkdir(out_filepath)
    # We now need to ensure that our files, while extant, contain the information
    # required to compute the score. Individual errors are propagated via the
    # function.
    if not validate_input_file(
            input_fp=parameter_filepath,
            requested_scorers=requested_solvers,
    ):
        raise RuntimeError(f"Input File failed to pass validation. Exiting.")
    # We should now be good to go so we just move forward with parsing the input
    # data and sending it off to the requested solvers.
    gc = parse_sbol_xml_tree(sbol_filepath)
    network = NetworkGeneticCircuit(gc)
    requested_requirements = generate_requirement_classes(
        parameter_filepath, requested_solvers
    )
    scoring_map = get_scorer_map()
    for solver, requirement in zip(requested_solvers, requested_requirements):
        solver_class = scoring_map[solver]
        try:
            solver_obj = solver_class(network, requirement)
        except TypeError:
            solver_obj = solver_class(requirement)
        solver_obj.score()
        solver_obj.report()


@app.command()
def synthesize_logic_graph(
        input_fp: str,
        visualize_graph: bool = True,
        save_edgelist: bool = True,
        output_fp: str = None,
):
    if not os.path.exists(input_fp):
        raise RuntimeError(f'Unable to find {input_fp}. Please investigate.')
    fn = Path(input_fp).stem
    if Path(input_fp).suffix != '.v':
        raise RuntimeError(
            f'Input File {fn} does not seem to be a verilog '
            f'file. Please investigate.'
        )
    lnetwork = LogicNetwork(verilog_fp=input_fp)
    # Maybe I put a truth table here?
    if visualize_graph:
        lnetwork.plot_graph(save_file=True, output_filename=f'{fn}.jpg')
    if save_edgelist:
        if output_fp is None:
            output_fp = f'{fn}.edgelist'
        lnetwork.save_netlist(output_fp=output_fp)
    lnetwork.cleanup()


@app.command()
def visualize_edgelist(
        input_fp: str,
):
    if not os.path.exists(input_fp):
        raise RuntimeError(f'Unable to find {input_fp}. Please investigate.')
    fn = Path(input_fp).stem
    if Path(input_fp).suffix != '.edgelist':
        raise RuntimeError(
            f'Input File {fn} does not seem to be a verilog '
            f'file. Please investigate.'
        )
    plot_cell_edgelist(input_fp)


if __name__ == "__main__":
    app()

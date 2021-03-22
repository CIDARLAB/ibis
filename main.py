"""
--------------------------------------------------------------------------------
Description:
Primary Entrypoint into <scoring-project>

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import os
import time
from typing import (
    List,
    Optional,
)

import pkg_resources
import typer
from rich.console import Console

from ibis.ingress import parse_sbol_xml_tree
from ibis.scoring import (
    get_requirement_map,
    get_scorer_description,
    generate_template_yaml,
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
    current_ver = pkg_resources.get_distribution('genetic-ibis').version
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

    Args:
        requested_solvers:
        output_fn:

    Returns:

    """
    if requested_solvers is not None:
        typer.echo(
            f"Generating template yaml file for all available solvers..."
        )
    else:
        typer.echo(
            f"Generating template yaml file for the following solvers:"
        )
        for solver in requested_solvers:
            typer.echo(
                f' - {solver}',
            )
    generate_template_yaml(
        requested_scorers=requested_solvers,
        output_fn=output_fn,
    )
    typer.echo(
        f'Template File {output_fn} written to {os.getcwd()}'
    )


@app.command()
def validate(
        input_fn: Optional[str] = "input.yml",
        verbose: Optional[bool] = False,
):
    """

    Args:
        input_fn:
        verbose:

    Returns:

    """
    if not os.path.isfile(input_fn):
        typer.echo(f"Unable to find {input_fn}. Please Investigate.")
        raise typer.Exit()



@app.command()
def solve(
        solver: str = typer.Argument(
            ...,
            help="The name of the solver",
            callback=name_callback,
            autocompletion=complete_name,
        ),
        in_filepath: str = typer.Argument(
            ...,
            help="Filepath: location of the SBOL file that constitutes the genetic "
                 "circuit",
        ),
        out_filepath: str = typer.Argument(
            ..., help="Filepath: location to write the output of the solved function"
        ),
        solver_info: Optional[bool] = typer.Option(
            None,
            "--info",
            "-i",
            help="Provides info on available solvers",
            callback=solver_details_callback,
            is_eager=True,
        ),
        version: Optional[bool] = typer.Option(
            None, "--version", "-v", callback=version_callback, is_eager=True
        ),
):
    """
    Takes an SBOL file, evaluates the quality of a genetic circuit, and then outputs performance metrics.
    """

    # Convert input-, output-paths to Path objects
    gc = parse_sbol_xml_tree(in_filepath)
    print(in_filepath)
    # Import necessary modules to do the thing

    # Here's a preliminary progress bar
    total = 0
    typer.echo(f"Processed {solver} solver.")


if __name__ == "__main__":
    app()

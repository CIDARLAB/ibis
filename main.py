"""
--------------------------------------------------------------------------------
Description:
Primary Entrypoint into <scoring-project>

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.style import Style

console = Console()
app = typer.Typer()

base_style = Style.parse("cyan")
console.print("Hello, World", style=base_style + Style(underline=True))

# TODO: For Eric-
# - Write a Commandline Interface that takes in the following input from the
# user from the commandline.
#       - [ ] The Name of the Solver
#       - [ ] The Filepath for the location of the SBOL file that constitutes
#           the genetic circuit. (You will need to worry about different OSes here)
#       - [ ] The filepath to write the output of the solved function to.


__version__ = "0.1.0"
valid_solvers = {
    "cello": {
        "description": "Built-in Cello module which predicts how well its circuits are likely to perform.",
    },
    "sleight": {
        "description": "Roughly evaluates the evolutionary stability of a circuit.",
    },
    "qian": {
        "description": "Calculates a intracellular resource demand coefficient for a circuit.",
    },
    "cummins": {
        "description": "Uses the DSGRN Database to summarize network dynamics of a circuit.",
    },
    "beal": {
        "description": "Characterizes the efficacy of a circuit based on signal-to-noise ratio.",
    },
    "gedeon": {
        "description": "Ranks a circuit by how robustly it supports hysteresis.",
    },
}


def name_callback(value: str):
    """
    Checks whether the first input argument is a valid solver.
    """
    if value.lower() not in valid_solvers.keys():
        raise typer.BadParameter("Solver not identified")
    return value


def solver_details_callback(value: bool):
    """
    Provides a brief description of each solver.
    """
    if value:
        typer.secho("Available Solvers...", fg=typer.colors.GREEN)
        for solver in valid_solvers.keys():
            typer.echo(f"{solver}: {valid_solvers[solver]['description']}")
        raise typer.Exit()


def version_callback(value: bool):
    """
    Returns version of scoring-project when the --version or -v options are called.
    """
    if value:
        typer.echo(f"CLI Version: {__version__}")
        raise typer.Exit()


def complete_name(incomplete: str):
    for name, help_text in valid_solvers:
        if name.startswith(incomplete):
            yield name, help_text


def solving_progress():
    """
    Let's imagine this tracks the progress of our solver, not a range().
    """
    for i in range(100):
        yield i


def convert_to_path_obj(in_filepath, out_filepath):
    cwd = Path.cwd()  # Specify where you are
    # You are gonna run into issues here if these don't exist.
    # You need to check to see if they exist, and if they don't you need to make them.
    # Also, depending on the system this is being run on, the python kernel might not
    # have permission to generate these directories. Something to think about.
    input_loc = cwd / "ingress"
    output_loc = cwd / "output"
    return input_loc, output_loc


@app.command()
def main(
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
    in_filepath, out_filepath = convert_to_path_obj(in_filepath, out_filepath)

    # Import necessary modules to do the thing

    # Here's a preliminary progress bar
    total = 0
    with typer.progressbar(
        solving_progress(), length=100, label="Processing"
    ) as progress:
        for value in progress:
            # Fake processing time
            time.sleep(0.03)
            total += 1
    typer.echo(f"Processed {solver} solver.")


if __name__ == "__main__":
    app()

'''
--------------------------------------------------------------------------------
Description:
Primary Entrypoint into <scoring-project>

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
'''
from rich.console import Console
from rich.style import Style

from datastucture import GeneticCircuit

console = Console()

base_style = Style.parse("cyan")
console.print("Hello, World", style=base_style + Style(underline=True))

import click

# TODO: For Eric-
# - Write a Commandline Interface that takes in the following input from the
# user from the commandline.
#       - [ ] The Name of the Solver
#       - [ ] The Filepath for the location of the SBOL file that constitutes
#           the genetic circuit. (You will need to worry about different OSes here)
#       - [ ] The filepath to write the output of the solved function to.


@click.command()
@click.option('--solver', default="cello", help='Which Solver to Use.')
def main_entry(solver: str, filepath: str, output_directory: str):
    '''

    Args:
        solver:

    Returns:

    '''
    print(f'{solver=}')


if __name__ == '__main__':
    main_entry()

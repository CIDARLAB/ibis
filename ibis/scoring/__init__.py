"""
--------------------------------------------------------------------------------
<Circuit-Scoring Project>

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from .scorer import (
    BaseScoring,
    BaseRequirement,
    get_requirement_map,
    get_scorer_description,
    get_score_association,
    generate_template_yaml,
    get_available_scorers,
    get_scorer_map,
    validate_input_file,
    generate_requirement_classes,
)
from .cello_score import CelloScoring

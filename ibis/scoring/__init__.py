"""
--------------------------------------------------------------------------------
<Circuit-Scoring Project>

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from .scorer import (
    BaseScoring,
    BaseRequirement,
    get_scorer_map,
    get_scorer_description,
    get_score_association,
    generate_template_yaml,
)
from .cello_score import CelloScoring

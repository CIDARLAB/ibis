"""
--------------------------------------------------------------------------------
Description:
Scores a a genetic circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import abc
import inspect
from typing import List

import yaml


# --------------------------- Requirement Base Class ---------------------------
# All Requirement classes should inherit from this base class.
#
# The child classes represent the unique requirements associated for an
# associated solver. These could be some sort of string for a file path,
# some sort of numerical score associated with parts, etc. These child classes
# are going to be aggregated by a top level authority and be used for generating
# a composite super datastructures for the purpose of checking the possibilities
# of what circuit scoring metrics are available to the user depending on their
# input data.
#
# The point is that this should strive to be as flexible as possible
# given the fragmentation within the scientific space. We'll attempt to enforce
# type checking at the top level, but I think that any kind of enforcement on a
# field by field basis is going to lead to us ripping our hair out.


class BaseRequirement(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        required_methods = [
            "validate",
            "get_required_inputs",
        ]
        subclass_reqs = True
        for method in required_methods:
            # Ensures that the class has the required function as an attribute
            subclass_reqs = subclass_reqs & hasattr(method, subclass)
            # Ensure that the attribute is a function
            fn = getattr(subclass, method)
            subclass_reqs = subclass_reqs & callable(fn)
        return subclass_reqs

    @abc.abstractmethod
    def validate(self):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_required_inputs(self):
        """Extract text from the data set"""
        raise NotImplementedError


def get_score_association(scorer_name: str) -> BaseRequirement:
    """

    Args:
        scorer_name:

    Returns:

    """
    # This import pattern is technically bad form, but I think it should be fine
    # for our initial attempt.
    from .cello_score import CelloRequirement

    score_map = {
        "cello": CelloRequirement,
    }
    if scorer_name not in list(score_map.keys()):
        raise RuntimeError(
            f"Unable to locate requirements for {scorer_name}. Please Investigate."
        )
    return score_map[scorer_name]


def generate_template_yaml(
        requested_scorers: List[str],
        output_fn: str = "example_input.yml",
):
    # This import pattern is technically bad form, but I think it should be fine
    # for our initial attempt.
    from ibis.scoring.cello_score import CelloRequirement

    score_map = {
        "cello": CelloRequirement,
    }
    for scorer in requested_scorers:
        if scorer not in list(score_map.keys()):
            raise RuntimeError(
                f"{scorer} is not recognized as a valid scoring metric. Valid"
                f"scoring metrics are {score_map.keys()}"
            )
    requirement_dict = {}
    for scorer in requested_scorers:
        # ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴゴ ゴ ゴ ゴ ゴ ゴ ゴ
        # I'll take things that would get me fired from a real job for 300 Alex.
        requirement_dict[scorer] = {}
        requirements = score_map[scorer]
        req_annotations = inspect.getdoc(requirements)
        sig_annotations = inspect.signature(requirements)
        raw_annotations = list(
            filter(
                lambda x: len(x) > 1,
                req_annotations.replace("    ", "").split("Args:")[1].splitlines(),
            )
        )
        annotation_dict = {}
        for line in raw_annotations:
            key, value = line.split(':')
            annotation_dict[key] = value
        if not list(sig_annotations.parameters.keys()) == list(annotation_dict.keys()):
            raise RuntimeError(
                'Argument annotations are incorrect for this scoring module.'
                'Please Investigate.'
            )
        for req in sig_annotations.parameters:
            requirement_dict[scorer][req] = annotation_dict[req]
    with open(output_fn, 'w') as out_file:
        yaml.dump(requirement_dict, out_file)


# ----------------------------- Scoring Base Class -----------------------------
# A scorer represents some sort of quality metric applied to a genetic circuit.
# Each scorer abstracts the implementation details behind a unified interface,
# where each of the only public methods available are described below:


class BaseScoring(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        required_methods = [
            "score",
            "get_requirements",
        ]
        subclass_reqs = True
        for method in required_methods:
            # Ensures that the class has the required function as an attribute
            subclass_reqs = subclass_reqs & hasattr(method, subclass)
            # Ensure that the attribute is a function
            fn = getattr(subclass, method)
            subclass_reqs = subclass_reqs & callable(fn)
        return subclass_reqs

    @abc.abstractmethod
    def score(self):
        """Load in the data set"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_requirements(self):
        """Extract text from the data set"""
        raise NotImplementedError


if __name__ == "__main__":
    scorers = ["cello"]
    generate_template_yaml(scorers)

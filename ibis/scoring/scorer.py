"""
--------------------------------------------------------------------------------
Description:
Scores a a genetic circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
import abc
import inspect
import os
from typing import (
    Dict,
    List,
    Optional,
    Type,
)

import yaml

from ibis.datastucture.circuits import NetworkGeneticCircuit, NetworkGeneticNode


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
        """

        Args:
            subclass:

        Returns:

        """
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
        """

        Returns:

        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_required_inputs(self):
        """

        Returns:

        """
        raise NotImplementedError

    def get_description(self) -> str:
        """

        Returns:

        """
        req_annotations = inspect.getdoc(self)
        description_string = req_annotations.split("\n\n")[0].replace("\n", " ")
        return description_string


def get_requirement_map() -> Dict[str, Type[BaseRequirement]]:
    """
    Primary entry-point for our 'modular' solvers. A new solver should only
    have to have it's relative import statement added here and have an entry
    in the solver map dictionary

    Returns:

    """
    from ibis.scoring.cello_score import CelloRequirement

    requirement_map = {
        "cello": CelloRequirement,
    }
    return requirement_map


# ----------------------------- Scoring Base Class -----------------------------
# A scorer represents some sort of quality metric applied to a genetic circuit.
# Each scorer abstracts the implementation details behind a unified interface,
# where each of the only public methods available are described below:


class BaseScoring(metaclass=abc.ABCMeta):
    def __init__(
        self,
        network_graph: NetworkGeneticCircuit,
        requirements: BaseRequirement,
    ):
        self.network_graph = network_graph
        self.requirements = requirements

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


# ------------------------- Scoring Utility Functions --------------------------
# Various utilities that allow attribute access or retrieve specific information
# from any of the modular solvers.
def get_scorer_map() -> Dict[str, Type[BaseScoring]]:
    """
    Primary entry-point for our 'modular' solvers. A new solver should only
    have to have it's relative import statement added here and have an entry
    in the solver map dictionary

    Returns:

    """
    from ibis.scoring.cello_score import CelloScoring

    scoring_map = {
        "cello": CelloScoring,
    }
    return scoring_map


def get_available_scorers() -> List:
    """

    Returns:

    """
    score_map = get_scorer_map()
    return list(score_map.keys())


def get_scorer_description():
    """

    Returns:

    """
    score_map = get_requirement_map()
    ret_list = []
    for scorer in score_map:
        scr = score_map[scorer]()
        scr_name = scr.__class__.__name__.replace("Requirement", "")
        ret_list.append(f"{scr_name}: {scr.get_description()}")
    return ret_list


def get_score_association(scorer_name: str) -> Type[BaseRequirement]:
    """

    Args:
        scorer_name:

    Returns:

    """
    # This import pattern is technically bad form, but I think it should be fine
    # for our initial attempt.
    score_map = get_requirement_map()
    if scorer_name not in list(score_map.keys()):
        raise RuntimeError(
            f"Unable to locate requirements for {scorer_name}. Please Investigate."
        )
    return score_map[scorer_name]


def generate_template_yaml(
    requested_scorers: Optional[List[str]] = None,
    output_fn: str = "input.yml",
):
    """

    Args:
        requested_scorers:
        output_fn:

    Returns:

    """
    # This import pattern is technically bad form, but I think it should be fine
    # for our initial attempt.
    req_map = get_requirement_map()
    if not requested_scorers:
        requested_scorers = req_map.keys()
    for scorer in requested_scorers:
        if scorer not in list(req_map.keys()):
            raise RuntimeError(
                f"{scorer} is not recognized as a valid scoring metric. Valid"
                f"scoring metrics are {req_map.keys()}"
            )
    requirement_dict = {}
    for scorer in requested_scorers:
        # ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴ ゴゴ ゴ ゴ ゴ ゴ ゴ ゴ
        # I'll take things that would get me fired from a real job for 300 Alex.
        requirement_dict[scorer] = {}
        requirements = req_map[scorer]
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
            key, value = line.split(":")
            annotation_dict[key] = value
        if not list(sig_annotations.parameters.keys()) == list(annotation_dict.keys()):
            raise RuntimeError(
                "Argument annotations are incorrect for this scoring module."
                "Please Investigate."
            )
        for req in sig_annotations.parameters:
            requirement_dict[scorer][req] = annotation_dict[req]
    with open(output_fn, "w") as out_file:
        yaml.dump(requirement_dict, out_file)


def validate_input_file(input_fp: str, requested_scorers: List[str]):
    if not os.path.isfile(input_fp):
        raise RuntimeError(
            f"{input_fp} is not a recognized filename. Please investigate."
        )
    # Generate our template file...
    req_map = get_requirement_map()
    requirement_dict = {}
    with open(input_fp, "r") as input_file:
        input_dict = yaml.load(input_file, Loader=yaml.FullLoader)
        # Aggregate all of our required scoring metrics.
        for scorer in requested_scorers:
            requirements = req_map[scorer]
            req_annotations = inspect.signature(requirements).parameters
            anno_dict = {}
            for k in req_annotations:
                anno = req_annotations[k].annotation
                anno_dict[k] = anno
            requirement_dict[scorer] = anno_dict
        # Not purposefully contained within the loop because we might have to
        # do some additional calculation or pulling at this point.
        # Now we validate each of the metrics.
        for key in input_dict:
            # Shouldn't be able to get here, but just in case.
            if key not in requirement_dict:
                raise RuntimeError(
                    f"Unable to find entry for {key}. Please Investigate"
                )
            sub_entry_dict = input_dict[key]
            sub_requirement_dict = requirement_dict[key]
            if sub_entry_dict.keys() != sub_requirement_dict.keys():
                diff = set(sub_requirement_dict.keys()) - set(sub_entry_dict)
                raise RuntimeError(
                    f"Input Dictionary and Requirements differ. Delta is {diff}"
                )
            for entry in sub_entry_dict:
                field_type = sub_requirement_dict[entry]
                # Some of these might require a cast because how they are
                # persisted to the file might differ from it's type in Python
                # space.
                actual_field = sub_entry_dict[entry]
                if type(actual_field) != field_type:
                    try:
                        field_type(actual_field)
                    except ValueError:
                        raise RuntimeError(
                            f"{key}: Field {actual_field} in {entry} is not of "
                            f"type {field_type}. Please investigate"
                        )
        return True


def generate_requirement_classes(input_fp: str, requested_scorers: List[str]):
    if not os.path.isfile(input_fp):
        raise RuntimeError(
            f"{input_fp} is not a recognized filename. Please investigate."
        )
    req_map = get_requirement_map()
    out_list = []
    with open(input_fp, "r") as input_file:
        input_dict = yaml.load(input_file, Loader=yaml.FullLoader)
        for scorer in requested_scorers:
            requirements = req_map[scorer]
            input_keys_for_requirement = input_dict[scorer]
            requirement_cls = requirements(**input_keys_for_requirement)
            out_list.append(requirement_cls)
    return out_list


if __name__ == "__main__":
    print(get_scorer_description())

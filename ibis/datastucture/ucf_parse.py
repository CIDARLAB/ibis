"""
--------------------------------------------------------------------------------
Description:
Datastructure describing the various attributes of a Genetic Circuit

Written by W.R. Jackson, Ben Bremer, Eric South
--------------------------------------------------------------------------------
"""
from collections import namedtuple
import copy
import dataclasses
import os
import json
from typing import (
    Dict,
    List,
)

import sympy


@dataclasses.dataclass
class ResponseFunctionParameter:
    """"""

    parameter_name: str
    parameter_map: str


@dataclasses.dataclass
class SensorParameter:
    """"""

    name: str
    value: float
    description: str


@dataclasses.dataclass
class ResponseFunction:
    """"""

    function_name: str
    equation: str
    parameters: List[ResponseFunctionParameter]
    expression = None

    def __post_init__(self):
        self.equation = self.equation.replace("$STATE", "state")
        self.expression = sympy.sympify(self.equation)

    def calculate_score(
        self, state_input: float, sensor_constants: Dict[str, SensorParameter]
    ):
        # We want our primary equation to remain 'clean' but we need to mutate
        # the symbolic representation of the equation to get what we want.
        temp_resolve = copy.copy(self.expression)
        param_list = [["state", state_input]]
        for param in self.parameters:
            param_key = param.parameter_name
            param_value = sensor_constants[param_key].value
            param_list.append([param_key, param_value])
        return temp_resolve.subs(param_list)


@dataclasses.dataclass
class CelloInputSensor:
    """"""

    sensor_name: str
    response_function: ResponseFunction
    sensor_parameters: Dict[str, SensorParameter]
    sensor_output: List[str]

    def get_response_function(self):
        return self.response_function

    def get_score(self, state_input: float):
        return self.response_function.calculate_score(
            state_input=state_input,
            sensor_constants=self.sensor_parameters,
        )


@dataclasses.dataclass
class CelloInput:
    sensor_table: Dict[str, CelloInputSensor] = None

    def __post_init__(self):
        self.sensor_table = {}

    def add_sensor(self, name: str, sensor: CelloInputSensor):
        self.sensor_table[name] = sensor

    def get_sensor(self, sensor_name: str):
        return self.sensor_table[sensor_name]

    def get_available_sensors(self) -> List[str]:
        return list(self.sensor_table.keys())

    def get_response_function_for_sensor(self, sensor_name: str):
        return self.sensor_table[sensor_name].response_function

    def get_sensor_parameters_for_sensor(self, sensor_name: str):
        return self.sensor_table[sensor_name].sensor_parameters


def parse_cello_input_file(fp: str):
    if not os.path.isfile(fp):
        raise RuntimeError(f"Unable to locate input file {fp}, please investigate.")
    with open(fp, "r") as input_file:
        cello_input = CelloInput()
        raw_input_file: List[dict] = json.load(input_file)
        # Collect all possible input sensor names, and then aggregate them
        sensor_list = []
        SensorField = namedtuple("SensorField", ["name", "model", "structure"])
        for obj in raw_input_file:
            if "collection" in obj:
                if obj["collection"] == "input_sensors":
                    temp_sensor = SensorField(
                        obj["name"],
                        obj["model"],
                        obj["structure"],
                    )
                    sensor_list.append(temp_sensor)
        for sensor in sensor_list:
            # Name Parsing
            name = sensor.name
            # Model and Response Function Parsing
            sensor_model_label = sensor.model
            sensor_parameters = {}
            response_function = None
            for i in raw_input_file:
                # We assume no duplicates within the input file.
                if i["name"] == sensor_model_label:
                    # Get the response function for this sensor.
                    func_name = i["functions"]["response_function"]
                    for j in raw_input_file:
                        if j["collection"] == "functions":
                            if j["name"] == func_name:
                                parameter_list = []
                                for k in j["parameters"]:
                                    c_param = ResponseFunctionParameter(
                                        parameter_name=k["name"],
                                        parameter_map=k["map"],
                                    )
                                    parameter_list.append(c_param)
                                response_function = ResponseFunction(
                                    function_name=func_name,
                                    equation=j["equation"],
                                    parameters=parameter_list,
                                )
                    for l in i["parameters"]:
                        sensor_parameters[l["name"]] = SensorParameter(
                            name=l["name"],
                            value=l["value"],
                            description=l["description"],
                        )
            # Output
            sensor_outputs = None
            for i in raw_input_file:
                # We assume no duplicates within the input file.
                if i["name"] == sensor.structure:
                    sensor_outputs = i["outputs"]
            sensor_obj = CelloInputSensor(
                sensor_name=name,
                response_function=response_function,
                sensor_parameters=sensor_parameters,
                sensor_output=sensor_outputs,
            )
            cello_input.add_sensor(
                name=sensor.name,
                sensor=sensor_obj,
            )
    return cello_input


if __name__ == "__main__":
    fn = "../../tests/test_cello/test_ucf_files/Eco1C1G1T1.input.json"
    out = parse_cello_input_file(fn)
    sensor_list = out.get_available_sensors()
    print(sensor_list)
    for sensor in sensor_list:
        thing = out.get_sensor(sensor)
        print(thing.get_score(1))

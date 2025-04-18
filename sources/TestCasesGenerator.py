"""
This file is part of the Modular Differential Testing Project.

The Modular Differential Testing Project is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

The Modular Differential Testing Project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the source code. If not, see <https://www.gnu.org/licenses/>.
"""
import random
import string
import re
from sources.CustomException import *
from sources.LoggerConfig import logger

DEFAULT_PARAMETERS = {
    "int":{
        "min": -200,
        "max": 200
    },
    "float": {
        "min":-200.0,
        "max":200.0
    },
    "string_length":{
        "min": 3,
        "max": 15
    },
    "list_size":{
        "min": 2,
        "max": 5
    }
}

class TestCasesGenerator:
    def __init__(self):
        # Nothing required to be declared or initialized here
        pass

    def generate_test_cases(self, args: list, test_count: int = 25, test_parameters : dict = DEFAULT_PARAMETERS) -> list:
        '''
        Main function for generating test cases. Makes use of the functions below to generate the data
        '''
        test_cases = []

        if not args:
            return []

        for _ in range(test_count):
            test_case = []
            try:
                for arg in args:
                    if "list[" in arg:
                        type_structure = self.parse_type(arg)
                        test_case.append(str(self.generate_random_list(type_structure, test_parameters)))
                    else:
                        test_case.append(str(self.random_value(arg, test_parameters)))
            except Exception as e:
                raise GenerateTestCasesException(f"{str(e)}")
            test_cases.append(test_case)

        return test_cases

    '''
    Functions for generating random value from all supported types (in Python)
    '''
    def random_int(self, start : int = -200, end : int = 200) -> int:
        return random.randint(start, end)

    def random_float(self, start : float = -200.0, end : float = 200.0) -> float:
        return round(random.uniform(start, end), 3)

    def random_string(self, min_length : int = 3, max_length : int = 15) -> str:
        length = random.randint(min_length, max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def random_char(self) -> str:
        return random.choice(string.ascii_letters)

    def random_bool(self) -> bool:
        return random.choice([True, False])

    def random_value(self, arg: str, parameters: dict = DEFAULT_PARAMETERS):
        int_parameters= parameters.get("int", {})
        int_min = int_parameters.get("min", -200)
        int_max = int_parameters.get("max", 200)
        float_parameters = parameters.get("float", {})
        float_min = float_parameters.get("min", -200.0)
        float_max = float_parameters.get("max", 200.0)
        string_parameters = parameters.get("string", {})
        string_min = string_parameters.get("min", 3)
        string_max = string_parameters.get("max", 15)

        if int_min >= int_max or float_min >= float_max or string_min >= string_max:
            logger.error("Minimal value is larger than maximal value!")
            raise ValueError("Minimal value is larger than maximal value!")

        match arg:
            case "int":
                return self.random_int(int_min, int_max)
            case "string":
                return self.random_string(string_min, string_max)
            case "double" | "float":
                return self.random_float(float_min, float_max)
            case "bool":
                return self.random_bool()
            case "char":
                return self.random_char()
            case _:
                logger.error("Test Generator random_value: Type not found!")
                logger.error(arg)
                raise TypeNotFoundException("error: Type not found!")

    def parse_type(self, type_str: str) -> list:
        '''
        Helper function to parse a list type in a format easier for generating lists and nested lists
        '''
        type_str = type_str.replace(" ", "")
        open_brackets_count = type_str.count('[')

        type_in_brackets = re.search(r'\[(.*?)\]', type_str).group(1)
        result = type_in_brackets.replace('[', '').replace(']', '')
        for _ in range(open_brackets_count):
            result = ['list', result]
        return result

    def generate_random_list(self, type_structure : list, parameters: dict = DEFAULT_PARAMETERS) -> list:
        '''
        Recursive function for generating lists and nested lists. It needs a format provided by the parse_type function
        '''
        if not isinstance(type_structure, list) or type_structure[0] not in ["list"]:
            raise ValueError("Invalid structure format.")

        list_parameter = parameters.get("list", {})
        list_min = list_parameter.get("min", 2)
        list_max = list_parameter.get("max", 5)
        if list_min >= list_max:
            logger.error("minimal value is larger than maximal value!")
            raise ValueError("minimal value is larger than maximal value!")

        sub_type = type_structure[1]
        list_length = random.randint(list_min, list_max)

        if isinstance(sub_type, list) and sub_type[0] in ["list"]:
            return [self.generate_random_list(sub_type) for _ in range(list_length)]
        else:
            return [self.random_value(sub_type) for _ in range(list_length)]

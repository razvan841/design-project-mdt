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
import os,sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.languages.Language import Language
from sources.Injector import Injector
from sources.DockerMaker import DockerMaker
from sources.LoggerConfig import logger
from sources.CustomException import *

class PyLanguage(Language):
    class PyInjector(Injector):
        '''
        Injector implementation for the Python scripting language.
        '''
        def __init__(self):
            super().__init__()
            self.ENDLINE = ""
            self.PRINT_RAW = "print(\var)"
            self.CAST_RAW = "\type(\var)"
            self.ARGS = "sys.argv[\index]"
            self.ARG_OFFSET = 1
            self.LIST_CAST = "ast.literal_eval(\var)"
            self.CAST_BOOL = "\var.lower()==\"true\""

        def declare(self, signature: dict) -> str:
            '''
            Python does not need to declare variables
            '''
            return ""

        def setup(self, signature: dict) -> str:
            return "import sys,ast\ndef main():\n"

        def wrap(self, signature: dict) -> str:
            return "if __name__ == \"__main__\":\n\tmain()"

        def cast(self, arg, type) -> str:
            match type:
                case "list":
                    return self.LIST_CAST.replace(self.ESCAPE_VAR,arg)
                case "bool":
                    return self.CAST_BOOL.replace(self.ESCAPE_VAR,arg)
                case _:
                    return super().cast(arg, type)
    class PyDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def add_base_image(self, version : str, compiler : str) -> str:
            if version == "":
                logger.warning("Python add_base_image: Didn't match any version, using 3.10!")
                return f"FROM python:3.10-alpine\n\n"
            return f"FROM python:{version}-alpine\n\n"

        def add_libraries(self, version : str, compiler : str, specs : list) -> str:
            if specs:
                return "RUN pip install " + " ".join(specs) + "\n\n"
            return ""

    def __init__(self):
        super().__init__()
        self.injector = PyLanguage.PyInjector()
        self.docker_maker = PyLanguage.PyDockerMaker()
        self.extension = "py"
        self.available_versions = ["2.7", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "3.12"]
        self.available_compilers = []
        # Python doesn't support double or char, so fall back to supported types
        self.type_dict = {
                "int": "int",
                "string": "str",
                "char": "str",
                "float": "float",
                "double": "float",
                "bool": "bool"
            }

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ['python', f'{function_name}.py']
        return command + input

    def generate_compile_command(self, function_name, compiler) -> list:
        return ["echo", "compiled"]

    def parse_type(self, type_str: str) -> str:
        return "list"
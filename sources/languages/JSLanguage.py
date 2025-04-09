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

class JSLanguage(Language):
    class JSInjector(Injector):
        '''
        Injector implementation for the Python scripting language.
        '''
        def __init__(self):
            super().__init__()
            self.ENDLINE = ""
            self.PRINT_RAW = "console.log(\var)"
            self.CAST_RAW = "\type(\var)"
            self.ARGS = "process.argv[\index]"
            self.ARG_OFFSET = 2
            self.LIST_CAST = "JSON.parse(\var)"
            self.CAST_BOOL = "\var.toLowerCase()===\"true\""
            self.CAST_INT = "parseInt(\var)"
            self.CAST_FLOAT = "parseFloat(\var)"
            self.CAST_STRING = "String(\var)"

        def declare(self, signature: dict) -> str:
            '''
            JavaScript does not need to declare variables
            '''
            return ""

        def setup(self, signature: dict) -> str:
            return ""

        def wrap(self, signature: dict) -> str:
            return ""

        def cast(self, arg : str, type : str) -> str:
            match type:
                case "list":
                    return self.LIST_CAST.replace(self.ESCAPE_VAR,arg)
                case "bool":
                    return self.CAST_BOOL.replace(self.ESCAPE_VAR,arg)
                case "int":
                    return self.CAST_INT.replace(self.ESCAPE_VAR,arg)
                case "float":
                    return self.CAST_FLOAT.replace(self.ESCAPE_VAR,arg)
                case "string":
                    return self.CAST_STRING.replace(self.ESCAPE_VAR,arg)
                case _:
                    return super().cast(arg, type)
    class JSDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def add_base_image(self, version: str, compiler : str):
            if version == "":
                logger.warning("JS add_base_image: Didn't match any version, using node:19!")
                return f"FROM node:19-alpine\n\n"
            return f"FROM {version}-alpine\n\n"

        def add_libraries(self, version : str, compiler : str, specs : list):
            if specs:
                return "RUN npm install " + " ".join(specs) + "\n\n"
            return ""

    def __init__(self):
        super().__init__()
        self.injector = JSLanguage.JSInjector()
        self.docker_maker = JSLanguage.JSDockerMaker()
        self.available_versions = [ "node:current", "node:19", "node:18", "node:16", "node:14", "node:12"]
        self.available_compilers = []
        self.extension = "js"
        self.type_dict = {
                "int": "int",
                "string": "string",
                "float": "float",
                "bool": "bool"
            }

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ['node', f'{function_name}.js']
        return command + input

    def generate_compile_command(self, function_name, compiler) -> list:
        return ["echo", "compiled"]

    def parse_type(self, type_str: str):
        return "list"
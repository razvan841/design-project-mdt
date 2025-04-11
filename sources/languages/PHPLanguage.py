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

class PHPLanguage(Language):
    class PHPInjector(Injector):
        '''
        Injector implementation for the Python scripting language.
        '''
        def __init__(self):
            super().__init__()
            self.ENDLINE = ";"
            self.PRINT_RAW = "echo json_encode($\var)"
            self.CAST_RAW = "\type(\var)"
            self.ARGS = "$argv[\index]"
            self.ARG_OFFSET = 1
            self.LIST_CAST = "json_decode(\var, true)"
            self.CAST_BOOL = "filter_var(\var, FILTER_VALIDATE_BOOLEAN)"
            self.CAST_INT = "(int) (\var)"
            self.CAST_FLOAT = "(float) (\var)"
            self.CAST_STRING = "(string) (\var)"
            self.DOLLAR = "$"

        def declare(self, signature: dict) -> str:
            '''
            PHP does not need to declare variables
            '''
            return ""

        def setup(self, signature: dict) -> str:
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

        def inject(self, source_path: str, destination_path: str, signature: dict):
            code = "<?php\n"
            try:
                with open(source_path, "r") as input:
                    code += input.read().replace("<?php", "").replace("?>", "")
            except Exception as e:
                logger.error(f'PHP Language inject: Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')
            code += self.NEWLINE + self.NEWLINE
            code += self.setup(signature)
            code += self.declare(signature)
            code += self.initialize(signature)
            code += self.call(signature)
            code += self.print_result(signature)
            code += self.wrap(signature)
            try:
                with open(destination_path, "w") as output:
                    output.write(code)
            except Exception as e:
                logger.error(f'PHP Language inject: Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

        def wrap(self, signature: dict) -> str:
            return "\n?>"

        def initialize_item(self, name: str, type: str, arg_index: int):
            logger.warning(type)
            if type == "list":
                fix = f"$g{arg_index} = str_replace(\"'\", '\"', $argv[{arg_index}]);\n"
                assign = f"${name} = json_decode($g{arg_index}, true);\n"
                return fix + assign
            return self.DOLLAR + name + self.SEP + self.ASSIGN + self.SEP + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE

        def call(self, signature: dict) -> str:
            params = ""
            args = list(signature["args"].keys())
            for i in range(len(args)):
                params += self.DOLLAR
                params += args[i]
                if i < len(args) - 1:
                    params += self.COMMA
                    params += self.SEP
            return self.DOLLAR +  self.OUTPUT_NAME + self.SEP + self.ASSIGN + self.SEP + signature["name"] + "(" + params + ")" + self.ENDLINE + self.NEWLINE

    class PHPDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def add_base_image(self, version : str, compiler : str):
            if version == "":
                logger.warning("PHP add_base_image: Didn't match any version, using php:8.3!")
                return f"FROM php:8.3-alpine\n\n"
            return f"FROM {version}-cli-alpine\n\n"

        def add_libraries(self, version : str, compiler : str, specs : list):
            if specs:
                return "RUN composer require " + " ".join(specs) + "\n\n"
            return ""

    def __init__(self):
        super().__init__()
        self.injector = PHPLanguage.PHPInjector()
        self.docker_maker = PHPLanguage.PHPDockerMaker()
        self.available_versions = ["php:8.3", "php:7.4", "php:5.6"]
        self.available_compilers = []
        self.extension = "php"
        self.type_dict = {
                "int": "int",
                "string": "string",
                "float": "float",
                "bool": "bool"
            }

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ['php', f'{function_name}.php']
        return command + input

    def generate_compile_command(self, function_name, compiler) -> list:
        return ["echo", "compiled"]

    def parse_type(self, type_str: str):
        return "list"
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
from sources.DockerMaker import DockerMaker, EXECUTION_PATH
from sources.LoggerConfig import logger
from sources.CustomException import *

class TSLanguage(Language):
    class TSInjector(Injector):
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
            self.LIST_CAST = "JSON.parse(\var.replace(/'/g, '\"'))"
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

        def initialize_item(self, name: str, type: str, arg_index: int):
            '''
            Initialize an individual variable from its respective program argument
            '''
            return self.INDENT + "const " + name + self.SEP + self.ASSIGN + self.SEP + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE

        def call(self, signature: dict) -> str:
            '''
            Call the function
            '''
            params = ""
            args = list(signature["args"].keys())
            for i in range(len(args)):
                params += args[i]
                if i < len(args) - 1:
                    params += self.COMMA
                    params += self.SEP
            return self.INDENT + "const " + self.OUTPUT_NAME + self.SEP + self.ASSIGN + self.SEP + signature["name"] + "(" + params + ")" + self.ENDLINE + self.NEWLINE


    class TSDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> bool:
            '''
            function that generates the dockerfile, based on the requirements of the code cell
            this class is overridden in every specific language class
            '''
            try:
                content = ""
                content += self.add_base_image(version, compiler)
                content += self.add_tsnode(version, compiler)
                content += self.add_libraries(version, compiler, specs)
                content += self.add_workdir()
                content += self.copy_all()
                content += self.add_time(version, compiler)
                content += self.add_sleep_command()

                try:
                    session_path = os.path.join(EXECUTION_PATH, str(index))
                    if not os.path.exists(session_path):
                        os.makedirs(session_path)
                except OSError:
                    logger.error("DockerMaker generate_dockerfile: Failed to create mounting folder")
                    raise OSError("Failed to create mounting folder")

                dockerfile_path = os.path.join(session_path, "Dockerfile")
                try:
                    with open(dockerfile_path, "w", encoding="utf-8") as file:
                        file.write(content)
                except OSError:
                    logger.error("DockerMaker generate_dockerfile: Failed to write Dockerfile")
                    raise OSError("Failed to write Dockerfile")
            except Exception as e:
                logger.error(f"DockerMaker generate_dockerfile: {str(e)}")
                raise RuntimeError(e)

            return True

        def add_base_image(self, version: str, compiler : str):
            if version == "":
                logger.warning("JS add_base_image: Didn't match any version, using node:19!")
                return "FROM node:19-alpine\n\n"
            return f"FROM {version}-alpine\n\n"

        def add_libraries(self, version : str, compiler : str, specs : list):
            if specs:
                return "RUN npm install " + " ".join(specs) + "\n\n"
            return ""

        def add_tsnode(self, version: str, compiler : str):
            return "RUN npm install -g typescript ts-node\n\n"

    def __init__(self):
        super().__init__()
        self.injector = TSLanguage.TSInjector()
        self.docker_maker = TSLanguage.TSDockerMaker()
        self.available_versions = ["node:19", "node:18", "node:16", "node:14", "node:12"]
        self.available_compilers = []
        self.extension = "ts"
        self.type_dict = {
                "int": "int",
                "string": "string",
                "char": "string",
                "float": "float",
                "double": "float",
                "bool": "bool"
            }

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ['node', f'{function_name}.js']
        return command + input

    def generate_compile_command(self, function_name, compiler) -> list:
        return ['tsc', f'{function_name}.ts']

    def parse_type(self, type_str: str):
        return "list"
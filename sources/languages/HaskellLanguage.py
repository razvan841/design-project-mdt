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

import os,sys, re
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.languages.Language import Language
from sources.Injector import Injector
from sources.DockerMaker import DockerMaker, EXECUTION_PATH
from sources.CustomException import *
from sources.LoggerConfig import logger

class HaskellLanguage(Language):
    class HaskellInjector(Injector):
        '''
        Injector implementation for the Haskell programming language
        WARNING! Do not use Tabs. Haskell does not like tabs :(
        '''
        #TODO: Implement lists, I was to lazy to do it
        def __init__(self):
            super().__init__()
            self.ARG_OFFSET = 0
            self.PRINT_RAW = "print result"
            self.ARGS = "(args !! \index)"
            self.ENDLINE = ""

        def inject(self, source_path: str, destination_path: str, signature: dict) -> None:
            '''
            Inject a main function into a source code file
            '''
            try:
                with open(source_path, "r") as input:
                    code = input.read()
            except Exception as e:
                logger.error(f'Injector inject: Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')
            code = self.init() + code
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
                logger.error(f'Injector inject: Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

        def init (self) -> str:
            return "import System.Environment (getArgs)\n\n"

        def setup(self, signature: dict) -> str:
            return "main :: IO ()\nmain = do\n    args <- getArgs\n    "

        def initialize_item(self, name: str, type: str, arg_index: int) -> str:
            return name + self.SEP + self.ASSIGN + self.SEP + f"read (args !! {arg_index}) :: " + type + self.NEWLINE + self.SEP * 8

        def declare(self, signature):
            return ""

        def initialize(self, signature: dict) -> str:
            initializations = "let "
            args = signature["args"]
            for index, (arg, type) in enumerate(args.items()):
                initializations += self.initialize_item(arg, type, index + self.ARG_OFFSET)
            return initializations

        def call(self, signature: dict) -> str:
            params = ""
            args = list(signature["args"].keys())
            for i in range(len(args)):
                params += args[i]
                if i < len(args) - 1:
                    params += self.SEP
            return self.OUTPUT_NAME + self.SEP + self.ASSIGN + self.SEP + signature["name"] + self.SEP + params + self.ENDLINE + self.NEWLINE

        def print_result(self, signature: dict) -> str:
            return self.SEP * 4 + self.PRINT_RAW

    class HaskellDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> bool:
            '''
            Overrides the generate_dockerfile because the dockerfile for cpp requires extra commands
            '''
            try:
                content = ""
                content += self.add_base_image(version, compiler)
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
                    logger.error("Cpp Language generate_dockerfile: Failed to create mounting folder")
                    raise OSError("Failed to create mounting folder")

                dockerfile_path = os.path.join(session_path, "Dockerfile")
                try:
                    with open(dockerfile_path, "w", encoding="utf-8") as file:
                        file.write(content)
                except OSError:
                    logger.error("Cpp Language generate_dockerfile: Failed to write Dockerfile")
                    raise OSError("Failed to write Dockerfile")
            except Exception as e:
                logger.error(f"Cpp Language generate_dockerfile: {str(e)}")
                raise RuntimeError(e)

            return True

        def add_base_image(self, version: str, compiler: str) -> str:
            if not version:
                return "FROM haskell:9.4.7-slim\n\n"
            return f"FROM haskell:{version}-slim\n\n"

        def add_time(self, version: str, compiler: str) -> str:
            return "RUN apt-get update && apt-get install -y time\n\n"

        #TODO: Find a way to add libraries
        def add_libraries(self, version: str, compiler: str, specs: list) -> str:
            return ""

    def __init__(self):
        super().__init__()
        self.injector = HaskellLanguage.HaskellInjector()
        self.docker_maker = HaskellLanguage.HaskellDockerMaker()
        self.available_versions = ["9.4", "9.2", "9.0", "8.8"]
        self.available_compilers = []
        self.extension = "hs"
        self.type_dict = {
                "int": "Int",
                "string": "String",
                "char": "Char",
                "float": "Float",
                "double": "Double",
                "bool": "Bool"
            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        return ["echo", "compiled"]

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ["runhaskell", f"{function_name}.hs"]
        return command + input

    #TODO: Implement Haskell Lists
    def parse_type(self, type_str: str) -> str:
        return ""

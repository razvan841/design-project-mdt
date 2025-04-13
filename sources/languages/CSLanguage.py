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

class CSLanguage(Language):
    class CSInjector(Injector):
        '''
        Injector implementation for the CS programming language
        '''
        def __init__(self):
            super().__init__()
            self.PRINT_RAW = "Console.WriteLine(result)"
            self.OUTPUT_NAME = "var result"
            self.ARG_OFFSET = 1
            self.CAST_BOOL = "bool.Parse(\var)"
            self.CAST_INT = "int.Parse(\var)"
            self.CAST_FLOAT = "float.Parse(\var)"
            self.CAST_DOUBLE = "double.Parse(\var)"
            self.CAST_STRING = "\var"
            self.CAST_CHAR = "char.Parse(\var)"
            self.CAST_LIST= "JsonSerializer.Deserialize<"
            self.ESCAPE_VAR = "\var"
            self.ARGS = "args[\index]"

        def inject(self, source_path: str, destination_path: str, signature: dict):
            try:
                with open(source_path, "r") as input:
                    code = input.read().replace("using System;", "")
                    requirements, code = self.get_requirements(code)
            except Exception as e:
                logger.error(f'CS Language inject: Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')
            code = self.init(requirements) + code
            code += self.NEWLINE + self.NEWLINE
            code += self.add_main()
            code += self.initialize(signature)
            code += self.call(signature)
            code += self.print_result(signature)
            code += self.wrap(signature)
            try:
                with open(destination_path, "w") as output:
                    output.write(code)
            except Exception as e:
                logger.error(f'CS Language inject: Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

        def declare_item(self, name, type):
            return ""

        def add_main(self) -> str:
            return "static void Main(string[] args)\n\t{\n"

        def get_requirements(self, code: str):
            lines = code.splitlines()
            usings = []
            code_from_static = []
            found_static = False

            for line in lines:
                if not found_static:
                    if line.strip().startswith("using"):
                        usings.append(line.strip())
                    elif "static" in line:
                        found_static = True
                        code_from_static.append(line)
                else:
                    code_from_static.append(line)

            return usings, "\n".join(code_from_static)

        def init(self, requirements : str) -> str:
            system = "using System;\nusing System.Text.Json;\nusing System.Collections.Generic;\n"
            libraries = self.add_requirements(requirements)
            class_init = "class Program\n{\n\t"
            return system + libraries + class_init

        def add_requirements(self, requirements : str) -> str:
            code = ""
            for req in requirements:
                code += req + "\n"
            return code

        def cast(self, arg : str, type : str) -> str:
            match type:
                case "bool":
                    return self.CAST_BOOL.replace(self.ESCAPE_VAR,arg)
                case "int":
                    return self.CAST_INT.replace(self.ESCAPE_VAR,arg)
                case "float":
                    return self.CAST_FLOAT.replace(self.ESCAPE_VAR,arg)
                case "double":
                    return self.CAST_DOUBLE.replace(self.ESCAPE_VAR,arg)
                case "string":
                    return self.CAST_STRING.replace(self.ESCAPE_VAR,arg)
                case "char":
                    return self.CAST_CHAR.replace(self.ESCAPE_VAR,arg)
                case s if s.startswith("List"):
                    return self.CAST_LIST + type + f">({arg})"
                case _:
                    return super().cast(arg, type)

        def wrap(self, signature: dict) -> str:
            return "}\n}"

        def initialize_item(self, name: str, type: str, arg_index: int):
            return self.INDENT + type + self.SEP + name + self.SEP + self.ASSIGN + self.SEP + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE

        def initialize(self, signature: dict) -> str:
            initializations = ""
            args = signature["args"]
            for index, (arg, type) in enumerate(args.items()):
                initializations += self.initialize_item(arg, type, index + self.ARG_OFFSET)
            return initializations

    class CSDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> None:
            '''
            This implementation for the dockerfile is very different because C# needs to set up a project, it is way harder to compile and run just a file
            Technically, you can compile and run just a file with dotnet-script, but the code is very different than normal C#, so i decided to do it like this
            '''
            try:
                content = ""
                content += self.add_base_image(version, compiler)
                content += self.add_time(version, compiler)
                content += self.add_workdir()
                content += self.copy_all()
                content += self.add_dotnet_project()
                content += self.copy_files()
                content += self.rmProgram()
                content += self.app_dir()
                content += self.add_libraries(version, compiler, specs)
                content += self.appWorkdir()
                content += self.add_sleep_command()

                try:
                    session_path = os.path.join(EXECUTION_PATH, str(index))
                    if not os.path.exists(session_path):
                        os.makedirs(session_path)
                except OSError:
                    logger.error("CS Language generate_dockerfile: Failed to create mounting folder")
                    raise OSError("Failed to create mounting folder")

                dockerfile_path = os.path.join(session_path, "Dockerfile")
                try:
                    with open(dockerfile_path, "w", encoding="utf-8") as file:
                        file.write(content)
                except OSError:
                    logger.error("CS Language generate_dockerfile: Failed to write Dockerfile")
                    raise OSError("Failed to write Dockerfile")
            except Exception as e:
                logger.error(f"CS Language generate_dockerfile: {str(e)}")
                raise RuntimeError(e)

            return True

        def add_workdir(self):
            return "WORKDIR /app\n\n"

        def copy_all(self) -> str:
            return "COPY . .\n\n"

        def add_base_image(self, version: str = "8.0", compiler: str = "dotnet") -> str:
            return f"FROM mcr.microsoft.com/{compiler}/sdk:{version} AS build\n\n"

        def add_dotnet_project(self) -> str:
            return "RUN dotnet new console -n MyApp\n\n"

        def copy_files(self) -> str:
            return "RUN mv *.cs MyApp/\n\n"

        def app_dir(self) -> str:
            return "WORKDIR /app/MyApp\n\n"

        def rmProgram(self) -> str:
            return "RUN rm MyApp/Program.cs\n\n"

        def add_libraries(self, version: str, compiler: str, specs: list) -> str:
            return ""

        def add_time(self, version: str, compiler: str) -> str:
            return "RUN apt-get update && apt-get install -y time\n\n"

        def appWorkdir(self) -> str:
            return 'WORKDIR /app/MyApp\n\n'

    def __init__(self):
        super().__init__()
        self.injector = CSLanguage.CSInjector()
        self.docker_maker = CSLanguage.CSDockerMaker()
        self.available_versions = ["8.0", "7.0"]
        self.available_compilers = ["dotnet"]
        self.extension = "cs"
        self.type_dict = {
                "int": "int",
                "string": "string",
                "char": "char",
                "float": "float",
                "double": "double",
                "bool": "bool"
            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        return ["dotnet", "build"]

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ["dotnet", "run", "myapp"]
        return command + input
    #FIXME: List handling
    def parse_type(self, type_str: str):
        type_str = type_str.replace(" ", "")

        open_brackets = type_str.count("[")
        type_str = type_str.replace("list[", "List<").replace("[", "List<")
        type_str = type_str.replace("]", "")
        type_str += ">" * open_brackets
        return type_str

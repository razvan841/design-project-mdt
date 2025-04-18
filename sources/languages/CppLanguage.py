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

class CppLanguage(Language):
    class CppInjector(Injector):
        '''
        Injector implementation for the C++ programming language
        '''
        def __init__(self):
            super().__init__()
            self.helper_files = ["../resources/cast.cpp"]
            self.PRINT_RAW = "std::cout << \var << std::endl"
            self.ARGS = "argv[\index]"
            self.ARG_OFFSET = 1

        def inject(self, source_path: str, destination_path: str, signature: dict) -> None:
            '''
            Inject a main function into a source code file
            '''
            try:
                with open(source_path, "r") as input:
                    code = input.read()
            except Exception as e:
                logger.error(f'Cpp Language inject: Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')
            code = self.include() + code
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
                logger.error(f'Cpp Language inject: Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

        def include(self) -> str:
            '''
            Include necessary libraries for the cpp implementation to work
            '''
            return "#include <vector>\n#include <string>\n\n"

        def declare(self, signature: dict) -> str:
            '''
            A string stream is additionally declared to help with type casting
            '''
            return super().declare(signature)

        def initialize_item(self, name: str, type: str, arg_index: int) -> str:
            '''
            Uses a string stream for type casting as a general solution
            '''
            content = self.INDENT + name + " = " + f"cast<{type}>(argv[{arg_index}])" + self.ENDLINE + self.NEWLINE
            return content

        def setup(self, signature: dict) -> str:
            files = self.get_helper_filenames()
            setup_string = "#include <iostream>\n"
            for file in files:
                setup_string += f"#include \"{file}\"\n"
            setup_string += "int main(int argc, const char* argv[])\n{"
            return setup_string

        def wrap(self, signature: dict) -> str:
            '''
            Finish the program with an exit code and close }
            '''
            return "\treturn 0;\n\n}"

        def get_helper_filenames(self) -> list:
            """Extracts only the filenames (without path) from self.helper_files."""
            return [os.path.basename(file) for file in self.helper_files]

    class CppDockerMaker(DockerMaker):
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
                content += self.add_json()
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
            match compiler:
                case "gcc":
                    return "FROM gcc:latest\n\n"
                case "clang":
                    return "FROM silkeh/clang:latest\n\n"
                case _:
                    logger.warning("Cpp Language add_base_image: Didn't match any compiler, adding gcc:latest!")
                    return "FROM gcc:latest\n\n"
            return ""

        def add_libraries(self, version: str, compiler: str, specs: list) -> str:
            if specs:
                return "RUN apt-get update && apt-get install -y " + " ".join(specs) + "\n\n"
            return ""

        def add_time(self, version: str, compiler: str) -> str:
            '''
            base cpp image doesn't have the time module so we add it manually
            '''
            return "RUN apt-get update && apt-get install -y time\n\n"

        def add_json(self) -> str:
            '''
            in order to handle lists, we make use of this library
            '''
            return "RUN apt-get install -y nlohmann-json3-dev\n\n"

        def add_compile(self, version: str, compiler: str, function_name: str, specs: dict) -> str:
            match compiler:
                case "gcc":
                    return f"RUN g++ {function_name}_injected.cpp -o {function_name}_injected\n\n"
                case "clang":
                    return f"RUN clang++ -o {function_name}_injected {function_name}_injected.cpp\n\n"
                case _:
                    logger.warning("Cpp Language add_compile: Didn't match any compiler, adding gcc:latest!")
                    return f"RUN g++ {function_name}_injected.cpp -o {function_name}_injected\n\n"

    def __init__(self):
        super().__init__()
        self.injector = CppLanguage.CppInjector()
        self.docker_maker = CppLanguage.CppDockerMaker()
        self.helper_files = self.injector.helper_files
        self.available_versions = []
        self.available_compilers = ["gcc", "clang"]
        self.extension = "cpp"
        self.type_dict = {
                "int": "int",
                "string": "std::string",
                "float": "float",
                "bool": "bool",
                "double": "double",
                "char": "char"
            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        compiler="g++"
        match compiler_name:
            case "clang":
                compiler = "clang++"
            case "gcc", _:
                compiler = "g++"
        return [compiler, '-Wno-conversion-null', '-Wno-return-type' ,f'{function_name}.cpp', '-o', function_name]

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = [f"./{function_name}"]
        return command + input

    def parse_type(self, type_str: str):
        '''
        function to change the list[...] format to proper cpp vectors
        '''
        type_str = type_str.replace(" ", "")
        open_brackets = type_str.count("[")
        type_str = type_str.replace("list[", "std::vector<").replace("[", "std::vector<").replace("string", "std::string")
        type_str = type_str.replace("]", "")
        type_str += ">" * open_brackets
        return type_str

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

class RustLanguage(Language):
    class RustInjector(Injector):
        '''
        Injector implementation for the Rust programming language
        '''
        # TODO: Add list dependency
        def __init__(self):
            super().__init__()
            # self.helper_files = ["../resources/Cargo.toml"]
            self.ARG_OFFSET = 1
            self.PRINT_RAW = 'println!("{}", \var)'
            self.SIMPLE_CAST = '.parse().expect("Expected a different type!")'
            self.CAST_STRING = ".clone()"
            self.CAST_CHAR = '.chars().next().expect("Expected a char");'
            self.ARGS = "args[\index]"

        def inject(self, source_path: str, destination_path: str, signature: dict) -> None:
            '''
            Inject a main function into a source code file
            '''
            try:
                with open(source_path, "r") as input:
                    code = input.read().replace("use std::env;", "")
            except Exception as e:
                logger.error(f'Rust Language inject: Failed to open source code file {source_path} with error: {e}')
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
                logger.error(f'Rust Language inject: Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

        def include(self) -> str:
            return "use std::env;\n\n"

        def declare_item(self, name: str, type: str) -> str:
            return ""

        def setup(self, signature: dict) -> str:
            return "fn main() {\n\tlet args: Vec<String> = env::args().collect();\n\n"

        def initialize_item(self, name: str, type: str, arg_index: int) -> str:
            return self.INDENT + "let " + name + ": " + type  + self.SEP + self.ASSIGN + self.SEP + f"args[{arg_index}]"  + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE

        def cast(self, arg : str, type : str) -> str:
            match type:
                case "bool" | "i64" | "f64":
                    return self.SIMPLE_CAST.replace(self.ESCAPE_VAR,arg)
                case "String":
                    return self.CAST_STRING.replace(self.ESCAPE_VAR,arg)
                case "char":
                    return self.CAST_CHAR.replace(self.ESCAPE_VAR,arg)
                case _:
                    return super().cast(arg, type)

        def call(self, signature: dict) -> str:
            params = ""
            args = list(signature["args"].keys())
            for i in range(len(args)):
                params += args[i]
                if i < len(args) - 1:
                    params += self.COMMA
                    params += self.SEP
            return self.INDENT + "let " + self.OUTPUT_NAME + self.SEP + self.ASSIGN + self.SEP + signature["name"] + "(" + params + ")" + self.ENDLINE + self.NEWLINE

        def wrap(self, signature: dict) -> str:
            return "}"


    class RustDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> bool:
            '''
            Overrides the generate_dockerfile because the dockerfile for Rust requires extra commands (creating a cargo project)
            '''
            try:
                content = ""
                content += self.add_base_image(version, compiler)
                content += self.add_libraries(version, compiler, specs)
                content += self.add_workdir()
                content += self.copy_all()
                content += self.create_cargo_project(function_name)
                content += self.project_workdir()
                content += self.add_sleep_command()

                try:
                    session_path = os.path.join(EXECUTION_PATH, str(index))
                    if not os.path.exists(session_path):
                        os.makedirs(session_path)
                except OSError:
                    logger.error("Rust Language generate_dockerfile: Failed to create mounting folder")
                    raise OSError("Failed to create mounting folder")

                dockerfile_path = os.path.join(session_path, "Dockerfile")
                try:
                    with open(dockerfile_path, "w", encoding="utf-8") as file:
                        file.write(content)
                except OSError:
                    logger.error("Rust Language generate_dockerfile: Failed to write Dockerfile")
                    raise OSError("Failed to write Dockerfile")
            except Exception as e:
                logger.error(f"Rust Language generate_dockerfile: {str(e)}")
                raise RuntimeError(e)

            return True

        def add_base_image(self, version: str, compiler: str) -> str:
            if not version:
                return "FROM rust:1.84.0-alpine\n\n"
            return f"FROM {version}-alpine\n\n"

        # TODO: Add libraries to cargo project
        def add_libraries(self, version: str, compiler: str, specs: list) -> str:
            return ""

        def create_cargo_project(self, function_name: str) -> str:
            return f"RUN cargo new code && mv {function_name}_injected.rs code/src/main.rs\n\n"

        def project_workdir(self) -> str:
            return "WORKDIR /usr/src/app/code/src\n\n"

    def __init__(self):
        super().__init__()
        self.injector = RustLanguage.RustInjector()
        self.docker_maker = RustLanguage.RustDockerMaker()
        # self.helper_files = self.injector.helper_files
        self.available_versions = ["rust:1.84.0", "rust:1.82.0", "rust:1.76.0"]
        self.available_compilers = []
        self.extension = "rs"
        self.type_dict = {
                "int": "i64",
                "string": "String",
                "float": "f64",
                "bool": "bool",
                "double": "double",
                "char": "char"
            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        return ["rustc", "main.rs"]

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = ["./main"]
        return command + input

    # TODO: parse lists correctly
    def parse_type(self, type_str: str) -> str:
        return ""

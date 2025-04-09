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

from sources.Injector import Injector
from sources.DockerMaker import DockerMaker
from sources.LoggerConfig import logger
from sources.CustomException import *

class Language:
    def __init__(self):
        self.injector = Injector()
        self.docker_maker = DockerMaker()
        self.helper_files = []
        self.available_versions = []
        self.available_compilers = []
        self.extension = "txt"
        self.type_dict = {}

    def generate_run_command(self, function_name: str, input: list) -> list :
        return []

    def generate_compile_command(self, function_name: str, compiler: str) -> list :
        return []

    def inject(self, source_path: str, destination_path: str, signature: dict) -> None:
        self.injector.inject(source_path, destination_path, signature)

    def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> None:
        self.docker_maker.generate_dockerfile(version, compiler, function_name, specs, index)

    def get_available_versions(self) -> list:
        return self.available_versions

    def get_available_compilers(self) -> list:
        return self.available_compilers

    def get_extension(self) -> str:
        return self.extension

    def check_signature(self, signature : dict) -> dict:
        args = signature.get('args', [])
        return_type = signature.get('return', "")
        name = signature.get('name', "")
        if(isinstance(args, dict)):
            return signature
        new_args = {}
        new_return = None
        if not args:
            new_signature = {
                "name": name,
                "return": new_return,
                "args": new_args
            }
            return new_signature
        counter = 0

        for arg in args:
            if "list" in arg:
                new_args[f"x{counter}"] = self.parse_type(arg)
                counter += 1
            else:
                arg_type = self.type_dict.get(arg, "")
                new_args[f"x{counter}"] = arg_type
                if not arg_type:
                    logger.error(f"{self.extension} Language check_signature: Didn't match any argument type for arg: {arg}")
                    raise ArgumentNotFoundException("Didn't match any argument type")
                counter += 1

        if "list" in return_type:
            new_return = self.parse_type(return_type)
        else:
            new_return = self.type_dict.get(return_type, "")
            if not return_type:
                logger.error(f"{self.extension} Language check_signature: Didn't match any argument type for arg: {return_type}")
                raise ArgumentNotFoundException("Didn't match any argument type")

        new_signature = {
            "name": name,
            "return": new_return,
            "args": new_args
        }
        return new_signature

    def parse_type(self, type_str: str) -> str:
        return ""
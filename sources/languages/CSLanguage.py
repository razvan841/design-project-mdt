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
        Injector implementation for the C++ programming language
        '''
        def __init__(self):
            super().__init__()

        def inject(self, source_path: str, destination_path: str, signature: dict):
            pass

        def include(self):
            pass

        def declare(self, signature):
            pass

        def initialize_item(self, name: str, type: str, arg_index: int) -> str:
            pass

        def setup(self, signature: dict) -> str:
            pass

        def wrap(self, signature: dict) -> str:
            pass

        def get_helper_filenames(self) -> list:
            pass

    class CSDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> None:
            pass

        def add_base_image(self, version: str, compiler: str) -> str:
            pass

        def add_libraries(self, version: str, compiler: str, specs: list) -> str:
            pass

        def add_time(self, version: str, compiler: str) -> str:
            pass

        def add_json(self) -> str:
            pass

        def add_compile(self, version: str, compiler: str, function_name: str, specs: dict) -> str:
            pass
    #TODO:
    def __init__(self):
        super().__init__()
        self.injector = CSLanguage.CppInjector()
        self.docker_maker = CSLanguage.CppDockerMaker()
        self.helper_files = self.injector.helper_files
        self.available_versions = []
        self.available_compilers = []
        self.extension = "cs"
        self.type_dict = {

            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        pass

    def generate_run_command(self, function_name: str, input: list) -> list :
        pass

    def parse_type(self, type_str: str):
        pass

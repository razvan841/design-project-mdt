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
        Injector implementation for the CS programming language
        '''
        def __init__(self):
            super().__init__()


        def declare_item(self, name, type):
            return ""

        def add_main(self) -> str:
            return ""


        def wrap(self, signature: dict) -> str:
            return ""


    class RustDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def add_base_image(self, version: str, compiler: str) -> str:
            return ""

        def add_libraries(self, version: str, compiler: str, specs: list) -> str:
            return ""

    def __init__(self):
        super().__init__()
        self.injector = RustLanguage.RustInjector()
        self.docker_maker = RustLanguage.RustDockerMaker()
        self.available_versions = []
        self.available_compilers = []
        self.extension = ""
        self.type_dict = {

            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        return []

    def generate_run_command(self, function_name: str, input: list) -> list :
        return []

    def parse_type(self, type_str: str) -> str:
        return ""

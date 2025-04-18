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
from sources.CustomException import InjectException

class JavaLanguage(Language):

    class JavaInjector(Injector):
        '''
        Injector implementation for the Java language.
        '''
        def __init__(self):
            super().__init__()
            self.PARSE = ".parse\type(\var)"
            self.ENDLINE = (";")
            self.ARGS = "args[\index]"
            self.PRINT_RAW = "System.out.println(\var)"
            self.END_FUNCTION = "\n}\n"
            self.CAST_BOOL = "Boolean.parseBoolean(\var)"
            self.HELPER_FILES = ["../resources/parse.java"]
            self.CAST_INT = "Integer.parseInt(\var)"
            self.ESCAPE_CAST = "\cast"
            self.CAST_LIST = "parse.parseNestedArray(\var, \cast)"

        def cast(self, arg:str, type:str) -> str:

            if "List" in type:
                parser = self.get_parser(type)
                return f"({type}) " + self.CAST_LIST.replace(self.ESCAPE_VAR, arg).replace(self.ESCAPE_CAST, parser)

            match type:
                case "int":
                    return self.CAST_INT.replace(self.ESCAPE_VAR,arg)
                case "String":
                    return arg
                case _:
                    class_name = type.lower().capitalize()
                    return class_name + self.PARSE.replace(self.ESCAPE_TYPE, class_name).replace(self.ESCAPE_VAR, arg)

        def get_parser(self, type:str) -> str:
            list_start = "List<"
            list_end = ">"
            type = type.replace(list_start,"")
            type = type.replace(list_end,"")
            parser = "s -> "
            match type:
                case "Integer":
                    parser +=  self.CAST_INT.replace(self.ESCAPE_VAR,"s")
                case "String":
                    parser +=  "s"
                case _:
                    class_name = type.lower().capitalize()
                    parser += class_name + self.PARSE.replace(self.ESCAPE_TYPE, class_name).replace(self.ESCAPE_VAR, "s")

            return parser

        def add_imports(self, source_path : str) -> str:
            imports = "import java.util.List;\n"
            try:
                with open(source_path, "r") as file:
                    for line in file:
                        imports += line if "import" in line else ""
            except Exception as e:
                logger.error(f'Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')
            return imports

        def setup(self, signature:dict) -> str:
            name = signature['name']
            return "\n@SuppressWarnings(\"unchecked\")\n" + " public class " + f"{name}_injected" + " {public static void main(String[] args) {\n"

        def wrap(self, signature:dict) -> str:
            return ""


        def declare_item(self, name:str, type:str) -> str:
            if type == "string":
                    return self.INDENT + type.lower().capitalize() + self.SEP + name + self.ENDLINE + self.NEWLINE
            return super().declare_item(name, type)

        def inject(self, source_path: str, destination_path: str, signature: dict) -> None:
            '''
            Inject a main function into a source code file
            '''
            code = self.add_imports(source_path)
            code += self.setup(signature)
            code += self.declare(signature)
            code += self.initialize(signature)
            code += self.call(signature)
            code += self.print_result(signature)
            code += self.END_FUNCTION
            try:
                with open(source_path, "r") as file:
                    for line in file:
                        code += line if "import" not in line else ""
            except Exception as e:
                logger.error(f'Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')

            code += self.END_FUNCTION
            try:
                with open(destination_path, "w") as output:
                    output.write(code)
            except Exception as e:
                logger.error(f'Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

    class JavaDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def add_base_image(self, version:str, compiler:str) -> str:
            if version == "":
                logger.warning("Java add_base_image: Didn't match any version, using amazoncorretto:19!")
                return f"FROM amazoncorretto:19-alpine\n\n"
            match compiler:
                case "amazoncorretto":
                    return f"FROM amazoncorretto:{version}-alpine\n\n"
                case "temurin":
                    return f"FROM eclipse-temurin:{version}-alpine\n\n"
                case _:
                    logger.warning("Didn't match any compiler, adding amazoncorretto!")
                    return f"FROM amazoncorretto:latest-alpine\n\n"

        def add_compile(self, version : str, compiler : str, function_name : str, specs : list) ->str:

            return f"RUN javac parse.java {function_name}_injected.java\n\n"

    def __init__(self):
        super().__init__()
        self.injector = JavaLanguage.JavaInjector()
        self.docker_maker = JavaLanguage.JavaDockerMaker()
        self.helper_files = self.injector.HELPER_FILES
        self.available_versions = ["21","19","17"]
        self.available_compilers = ["amazoncorretto", "temurin"]
        self.extension = "java"
        self.type_dict = {
                "int": "int",
                "long": "long",
                "string": "String",
                "float": "float",
                "double": "double",
                "bool": "boolean",
                "char": "char"
            }


    def generate_compile_command(self, function_name:str, compiler:str) -> list:
        return ["javac" , "parse.java" ,f"{function_name}.java"]

    def generate_run_command(self, function_name:str, input:list) -> list:
        return ["java" , function_name] + input

    def parse_type(self, type_str: str) -> str:
        type_map = {
            "string": "String",
            "bool": "Boolean",
            "int": "Integer",
            "float": "Float",
            "char": "String",
            "double": "Double",
            "long": "Long",
            "short": "Short"
        }

        type_str = type_str.replace(" ", "")

        for old_type, new_type in type_map.items():
            type_str = type_str.replace(old_type, new_type)

        open_brackets = type_str.count("[")
        type_str = type_str.replace("list[", "List<").replace("[", "List<")
        type_str = type_str.replace("]", "")
        type_str += ">" * open_brackets
        return type_str


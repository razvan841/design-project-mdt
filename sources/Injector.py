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
import sys
import os
from sources.CustomException import InjectException

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from sources.LoggerConfig import logger
class Injector:
    '''
    Base Injector class for injecting a main function/function call into a raw source code file.
    This class can be inherited to implement additional programming languages.
    Injection assumes that most programming languages follow a similar structure towards a function call:
    open main, declare variables, initialize variables with program input arguments, call the function,
    print the result, wrap main. Each of the individual steps may be overridden in the inherited class to
    properly implement the language. Certain special characters/functions exist as attributes,
    which can also be overridden.
    '''
    def __init__(self):
        self.NEWLINE = "\n"
        self.INDENT = "\t"
        self.SEP = " "
        self.COMMA = ","
        self.ENDLINE = ";"
        self.CAST_RAW = ""
        self.PRINT_RAW = ""
        self.ASSIGN = "="
        self.ESCAPE_VAR = "\var"
        self.ESCAPE_TYPE = "\type"
        self.ARGS = ""
        self.ESCAPE_INDEX = "\index"
        self.OUTPUT_NAME = "result"
        self.ARG_OFFSET = 0

    def inject(self, source_path: str, destination_path: str, signature: dict):
        '''
        Inject a main function into a source code file
        '''
        try:
            with open(source_path, "r") as input:
                code = input.read()
        except Exception as e:
            logger.error(f'Injector inject: Failed to open source code file {source_path} with error: {e}')
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
            logger.error(f'Injector inject: Failed to write to destination {destination_path} with error: {e}')
            raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

    def setup(self, signature: dict) -> str:
        '''
        Setup the program. (i.e. declare main function/imports)
        '''
        return ""

    def declare_item(self, name: str, type: str) -> str:
        '''
        Declare an individual variable
        '''
        return self.INDENT + type + self.SEP + name + self.ENDLINE + self.NEWLINE

    def declare(self, signature: dict) -> str:
        '''
        Declare all necessary variables to be able to call the function
        '''
        declarations = self.NEWLINE
        args = signature["args"]
        for arg, type in args.items():
            declarations += self.declare_item(arg, type)

        declarations += self.declare_item(self.OUTPUT_NAME, signature["return"])

        return declarations

    def cast(self, arg: str, type: str) -> str:
        '''
        Cast program input argument into the proper type
        '''
        return self.CAST_RAW.replace(self.ESCAPE_VAR, arg).replace(self.ESCAPE_TYPE, type)

    def get_arg(self, index: int) -> str:
        '''
        Obtain a program argument
        '''
        return self.ARGS.replace(self.ESCAPE_INDEX, str(index))

    def initialize_item(self, name: str, type: str, arg_index: int):
        '''
        Initialize an individual variable from its respective program argument
        '''
        return self.INDENT + name + self.SEP + self.ASSIGN + self.SEP + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE

    def initialize(self, signature: dict) -> str:
        '''
        Initialize all variables necessary to call the function
        '''
        initializations = ""
        args = signature["args"]
        for index, (arg, type) in enumerate(args.items()):
            initializations += self.initialize_item(arg, type, index + self.ARG_OFFSET)
        return initializations

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
        return self.INDENT + self.OUTPUT_NAME + self.SEP + self.ASSIGN + self.SEP + signature["name"] + "(" + params + ")" + self.ENDLINE + self.NEWLINE

    def print_result(self, signature: dict) -> str:
        '''
        Print function result
        '''
        return self.INDENT + self.PRINT_RAW.replace(self.ESCAPE_VAR, self.OUTPUT_NAME) + self.ENDLINE + self.NEWLINE

    def wrap(self, signature: dict) -> str:
        '''
        Wrap up the program (i.e. close main/deallocate resources/etc.)
        '''
        return ""

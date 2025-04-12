import os,sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.languages.Language import Language
from sources.Injector import Injector
from sources.DockerMaker import DockerMaker, EXECUTION_PATH
from sources.CustomException import *
from sources.LoggerConfig import logger

class GoLanguage(Language):
    '''
    Implementation of the Go Language
    For some reason, the parser accepts only int and not int64 and only float64 and not float
    Maybe i am just retarded
    Sadly, i didn't implement lists, there is not much support for it and the injecting such a parser would suck. Maybe with a helper file would be easier
    '''
    class GoInjector(Injector):
        '''
        Injector implementation for the C++ programming language
        '''
        def __init__(self):
            super().__init__()
            self.helper_files = []
            self.PRINT_RAW = 'fmt.Printf("%f\\n",\var)'
            self.ARGS = "os.Args[\index]"
            self.ARG_OFFSET = 1
            self.ASSIGN = ":="
            self.CAST_BOOL = "strconv.ParseBool(\var)"
            self.CAST_INT = "strconv.Atoi(\var)"
            self.CAST_FLOAT = "strconv.ParseFloat(\var, 64)"
            self.CAST_STRING = "\var"

        def inject(self, source_path: str, destination_path: str, signature: dict):
            '''
            Inject a main function into a source code file
            '''
            try:
                with open(source_path, "r") as input:
                    raw_code = input.read()
            except Exception as e:
                logger.error(f'Go Language inject: Failed to open source code file {source_path} with error: {e}')
                raise InjectException(f'Failed to open source code file {source_path} with error: {e}')
            code = self.include_import(raw_code, signature)
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
                logger.error(f'Go Language inject: Failed to write to destination {destination_path} with error: {e}')
                raise InjectException(f'Failed to write to destination {destination_path} with error: {e}')

        def include_import(self, code: str, signature : dict) -> str:
            lines = code.splitlines()

            inside_import_block = False
            import_lines = []
            args = signature.get("args", {})
            if all(value == "string" for value in args.values()):
                necessary_imports= {"fmt", "os"}
            else:
                necessary_imports = {"fmt", "os", "strconv"}

            user_imports = set()
            code_lines = []

            # Traverse through the lines and separate the import block and other code
            for i, line in enumerate(lines):
                if line.strip().startswith("import (") or line.strip().startswith("import("):
                    inside_import_block = True
                    import_lines.append(line)
                    continue
                if inside_import_block and line.strip() == ")":
                    inside_import_block = False
                    import_lines.append(line)
                    continue
                if inside_import_block:
                    import_lines.append(line)
                elif line.strip().startswith("package main"):
                    # Skip the package line, handle it separately later
                    continue
                else:
                    code_lines.append(line)

            # If the import block exists, collect libraries inside it
            if import_lines:
                raw_existing_imports = {line.strip().split()[0] for line in import_lines if line.strip() and not line.strip().startswith("//")}
                # Add necessary imports to the existing ones
                existing_imports = {s for s in raw_existing_imports if "import" not in s and ")" not in s}
                stripped_set = {item.replace('"', '').replace("'", "") for item in existing_imports}
                print(stripped_set)
                user_imports = stripped_set
            else:
                user_imports = set()

            # Combine necessary imports and user imports, ensuring no duplicates
            combined_imports = necessary_imports.union(user_imports)

            # Rebuild the code
            new_code = []

            # Add package main line
            new_code.append("package main")

            # Add import block with necessary and user libraries
            new_code.append("import (")
            for imp in sorted(combined_imports):  # Sorting imports (optional)
                new_code.append(f'\t"{imp}"')
            new_code.append(")")

            # Add the remaining code lines
            new_code.extend(code_lines)

            return '\n'.join(new_code)

        def declare(self, signature: dict) -> str:
            return ""

        def setup(self, signature: dict) -> str:
            setup_string = "func main() {\n"
            return setup_string

        def cast(self, arg, type):
            match type:
                case "bool":
                    return self.CAST_BOOL.replace(self.ESCAPE_VAR,arg)
                case "int":
                    return self.CAST_INT.replace(self.ESCAPE_VAR,arg)
                case "float64":
                    return self.CAST_FLOAT.replace(self.ESCAPE_VAR,arg)
                case "string":
                    return self.CAST_STRING.replace(self.ESCAPE_VAR,arg)
                case _:
                    return super().cast(arg, type)

        def wrap(self, signature: dict) -> str:
            return "\n}"

        def initialize_item(self, name: str, type: str, arg_index: int):
            '''
            Initialize an individual variable from its respective program argument
            '''
            if type != "string":
                assign = self.INDENT + name + self.COMMA + self.SEP + f"err{name}" + self.SEP + self.ASSIGN + self.SEP + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE
            else:
                 assign = self.INDENT + name + self.SEP + self.ASSIGN + self.SEP + self.cast(self.get_arg(arg_index), type) + self.ENDLINE + self.NEWLINE

            handle_error = ""
            if type == "float64" or type == "int" or type == "bool":
                handle_error = self.handle_error(name)

            return assign + handle_error

        def initialize(self, signature: dict) -> str:
            '''
            Initialize all variables necessary to call the function
            '''
            initializations = ""
            args = signature["args"]
            for index, (arg, type) in enumerate(args.items()):
                initializations += self.initialize_item(arg, type, index + self.ARG_OFFSET)
            return initializations

        def handle_error(self, name: str) -> str:
            check = f"\tif err{name} != nil " + "{\n"
            print_line = '\t\tfmt.Println("Invalid input. Please enter valid values.")\n\t\treturn\n\t}\n'
            return check + print_line

        def print_result(self, signature: dict) -> str:
            '''
            Print function result
            '''
            return_type = signature.get("return", "")
            a = "%s"
            match return_type:
                case "float64":
                    a = "%f"
                case "int":
                    a = "%d"
                case "string":
                    a = "%s"
                case "bool":
                    a = "%t"
            print_statement = self.INDENT + 'fmt.Printf("' + a + '",\var)'
            return print_statement.replace(self.ESCAPE_VAR, self.OUTPUT_NAME)



    class GoDockerMaker(DockerMaker):
        def __init__(self):
            super().__init__()

        def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: dict, index: int) -> None:
            try:
                content = ""
                content += self.add_base_image(version, compiler)
                content += self.add_workdir()
                content += self.copy_all()
                content += self.add_time(version, compiler)
                content += self.add_libraries(version, compiler, specs)
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

        def add_base_image(self, version: str, compiler: str = "gc") -> str:
            match compiler:
                case "gc":
                    return f"FROM golang:{version}-alpine\n\n"
                case _:
                    logger.warning("Go Language add_base_image: Didn't match any compiler, adding go:1.21!")
                    return f"FROM golang:1.21-alpine\n\n"
            return ""

        def add_libraries(self, version: str, compiler: str, specs: dict) -> str:
            libraries = specs.get("libraries", []) if isinstance(specs, dict) else []
            command = ""
            if libraries:
                command += "RUN go mod init project\n\n"
                command += "RUN go mod tidy\n\n"
            return command

        def add_compile(self, version: str, compiler: str, function_name: str, specs: dict) -> str:
            match compiler:
                case "gc":
                    return f"RUN go build -o {function_name}_injected {function_name}_injected.go\n\n"
                case _:
                    logger.warning("Go Language add_compile: Didn't match any compiler, using the gc compiler!")
                    return f"RUN go build -o {function_name}_injected {function_name}_injected.go\n\n"

    def __init__(self):
        super().__init__()
        self.injector = GoLanguage.GoInjector()
        self.docker_maker = GoLanguage.GoDockerMaker()
        self.helper_files = self.injector.helper_files
        self.available_versions = ["1.24", "1.22", "1.21", "1.19", "1.17"]
        self.available_compilers = ["gc"]
        self.extension = "go"
        self.type_dict = {
                "int": "int",
                "string": "string",
                "float": "float64",
                "bool": "bool"
            }

    def generate_compile_command(self, function_name: str, compiler_name: str) -> list:
        compiler = "go"
        return [compiler, 'build', f'{function_name}.go']

    def generate_run_command(self, function_name: str, input: list) -> list :
        command = [f"./{function_name}"]
        return command + input

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
import os,sys,shutil
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.DockerMaker import EXECUTION_PATH
from sources.Podman import Podman, podman
from sources.CustomException import *
from sources.LoggerConfig import logger, exec_logger
from sources.LanguageFactory import LanguageFactory

class Container:
    def __init__(self, metadata: dict, index: int, podman_instance: Podman = podman, run_as_is: bool = False):
        self.metadata = metadata
        self.available = True
        self.index = index
        self.podman = podman_instance
        self.run_as_is = run_as_is
        self.language = LanguageFactory().get_language(metadata['language'])
        try:
            # When creating a new container, first a Dockerfile is created.
            if self.run_as_is:
                function_name = "function"
                self.metadata['signature']['name'] = function_name
            self.create_dockerfile()
            exec_logger.info(f"Dockerfile done: {self.index}")
            self.mounting_path = os.path.join(EXECUTION_PATH,f'{index}')
            if not self.run_as_is:
                self.check_signature()
            # Injects user code into a file with a main function
            self.inject()
            exec_logger.info(f"Inject done: {self.index}")
            # Builds the image for the container
            self.copy_helper_files()
            self.podman.build_image(f'image_{index}', f'image_tag_{index}',mount_path=self.mounting_path)
            exec_logger.info(f"Build image done: {self.index}")
            # Runs image. This automatically creates a container.
            # No compilation is needed as it is specified within the Dockerfile
            # Assumption is made that you do not need to create a container without running it
            self.podman.run_image(image_name=f'image_{index}',tag=f'image_tag_{index}',container_name=f'container_{index}')
            exec_logger.info(f"Run image done: {self.index}")
            logger.debug(f"Container init: {self.language.helper_files}")

        except Exception as e:
            logger.debug(f"Container: {str(e)}")
            raise InitContainerException(e)

    def copy_helper_files(self) -> None:
        for file in self.language.helper_files:
            file_name = file.split('/')[-1]
            shutil.copy2(file,os.path.join(self.mounting_path,file_name))


    def create_dockerfile(self) -> None :
        '''
        Function to generate Dockerfile from given metadata. Will only be done once upon creation of a container image
        '''
        try:
            version = self.metadata['version']
            compiler = self.metadata['compiler']
            function_name = self.metadata['signature']['name']
            specs = self.metadata['specs']
            index = self.index
            self.language.generate_dockerfile(version=version, compiler=compiler, function_name=function_name, specs=specs, index=index)
            logger.debug(f"Container create_dockerfile: Created dockerfile for container {index}")
        except KeyError as e:
            logger.error(f"Container create_dockerfile: Missing required metadata key: {str(e)}")
        except Exception as e:
            logger.error(f"Container create_dockerfile: {str(e)}")

    def run_code(self, input: list, timeout: int = 60) -> dict :
        '''
        Function that runs code inside a container with the specified input.
        Called from ContainerManager class
        '''
        try:
            self.available = False
            command = self.generate_run_command(input=input)
            output =  self.podman.exec_command(f'container_{self.index}', command, metrics=True, timeout = timeout)
            # Container finished executing code and is now available again
            self.available = True
            exec_logger.info(f"Test instance done: {self.index}")
            return output
        except Exception as e:
            self.available = True
            raise RunCodeException(e)

    def compile_code(self) -> dict:
        '''
        Generates command to compile code inside of container.
        Used when injecting new code into container
        '''
        try:
            self.available = False
            command = self.generate_compile_command()
            output = self.podman.exec_command(f'container_{self.index}', command)
            self.available = True
            return output
        except Exception as e:
            self.available = True
            raise CompileCodeException(e)

    def generate_run_command(self, input: list ) -> str :
        '''
        Generates the run command used to run the code
        '''
        try:
            function_name = self.metadata['signature']['name'] + "_injected"
            return self.language.generate_run_command(function_name, input)
        except KeyError as e:
            logger.error(f"Container generate_run_command: Missing required metadata key: {e}")

    def generate_compile_command(self) -> str :
        '''
        Generates the compile command , needed for languages like C++
        '''
        try:
            function_name = self.metadata['signature']['name'] + "_injected"
            compiler = self.metadata['compiler']
            return self.language.generate_compile_command(function_name, compiler)
        except KeyError as e:
            logger.error(f"Container generate_compile_command: Missing required metadata key: {e}")

    def terminate(self) -> None:
        '''
        Deletes the container, its associated image, and the folder on which the container was mounted.
        '''
        try:
            self.podman.stop_container(f'container_{self.index}')
            self.podman.remove_container(f'container_{self.index}')
            self.podman.remove_image(f'image_{self.index}', f'image_tag_{self.index}')
            self.remove_folder()
        except Exception as e:
            raise TerminateException(e)

    def clear(self) -> None:
        '''
        Used to delete the code file inside the container, needed for when inputting new code
        '''
        try:
            self.available = False
            output = self.podman.exec_command(f'container_{self.index}', ['ls'])
            for file in output['stdout']:
                self.podman.exec_command(f'container_{self.index}', ['rm', file])
            self.remove_folder()
            self.available = True
        except Exception as e:
            raise ClearException(e)

    def remove_folder(self) -> None:
        '''
        Removes the folder where the container was mounted on
        '''
        try:
            files = os.listdir(self.mounting_path)
            for file in files:
                file_path = os.path.join(self.mounting_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(self.mounting_path)
        except Exception as e:
            raise OSError("Failed to remove folder")

    def inject(self) -> None:
        '''
        Injects user code into a main function with necessary inputs used to run
        '''
        code = self.metadata['code']
        signature = self.metadata.get("signature", {})
        function_name = signature.get('name', "")

        if not os.path.exists(self.mounting_path):
            os.makedirs(self.mounting_path)
        # Create basic file
        if self.run_as_is:
            function_name = "function"
            self.metadata['signature']['name'] = function_name
            file_name = os.path.join(self.mounting_path, f"{function_name}_injected.{self.language.get_extension()}")
            with open(file_name, "w") as file:
                file.write(code)
            return

        file_name = os.path.join(self.mounting_path, f"{function_name}.{self.language.get_extension()}")
        with open(file_name, "w") as file:
            file.write(code)
        dest_path = os.path.join(self.mounting_path, f"{function_name}_injected.{self.language.get_extension()}")
        # Create injected file
        self.language.inject(file_name, dest_path, signature)
        # Remove basic file
        if os.path.exists(file_name):
            os.remove(file_name)

    def change_code(self) -> None:
        '''
        Change code file inside the container
        '''
        try:
            self.available = False
            self.clear()
            if not self.run_as_is:
                self.check_signature()
            self.inject()
            self.copy_helper_files()
            self.upload_code()
            self.compile_code()
            self.available = True
            exec_logger.info(f"Dockerfile done: {self.index}")
            exec_logger.info(f"Inject done: {self.index}")
            exec_logger.info(f"Build done: {self.index}")
            exec_logger.info(f"Run done: {self.index}")
        except (ClearException, ChangeCodeException) as e:
            raise ContainerFileCommunicationException(e)
        except Exception as e:
            self.available = True
            raise ChangeCodeException(e)

    def upload_code(self) -> None:
        '''
        Uploads new user code to container
        '''
        files = os.listdir(self.mounting_path)
        for file in files:
            self.podman.copy_to_container(os.path.join(self.mounting_path, file), f"container_{self.index}")


    def set_metadata(self, metadata: dict) -> None:
        '''
        Sets the new metadata for the container.
        Used when recycling an old container that has the same language settings, but method signature is different
        '''
        self.metadata = metadata

    def is_available(self) -> bool:
        '''
        Getter for available flag
        '''
        return self.available

    def set_available(self, available: bool) -> None:
        '''
        Setter for available flag
        '''
        self.available = available

    def set_run_as_is(self, run_as_is: bool) -> None:
        '''
        Setter run_as_is flag
        '''
        self.run_as_is = run_as_is

    def check_signature(self) -> None:
        '''
        Transforms signature from list to dict, adding variable names too
        Signature depends on the language
        '''
        try:
            signature = self.metadata.get('signature', {})
            new_signature = self.language.check_signature(signature)
            self.metadata['signature'] = new_signature
        except ArgumentNotFoundException:
            raise ArgumentNotFoundException("argument type not found!")


def format_output(stdout: str = "", stderr: str = "") -> dict:
    '''
    format input strings to match output of exec_command
    '''
    return {
        "stdout": [stdout],
        "stderr": [stderr]
    }

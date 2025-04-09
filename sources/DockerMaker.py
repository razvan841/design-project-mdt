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

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from sources.LoggerConfig import logger

EXECUTION_PATH = os.path.join(parent_dir, "sessions")

class DockerMaker:
    def __init__(self):
        self.WORKDIR = "WORKDIR /usr/src/app\n\n"
        self.COPY_ALL = "COPY . /usr/src/app\n\n"
        self.SLEEP_COMMAND = 'CMD ["sleep", "365000d"]\n'

    def generate_dockerfile(self, version: str, compiler: str, function_name: str, specs: list, index: int) -> None:
        '''
        function that generates the dockerfile, based on the requirements of the code cell
        this class is overridden in every specific language class
        '''
        try:
            content = ""
            content += self.add_base_image(version, compiler)
            content += self.add_libraries(version, compiler, specs)
            content += self.add_workdir()
            content += self.copy_all()
            content += self.add_time(version, compiler)
            # content += self.add_compile(version, compiler, function_name, specs)
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

    def add_base_image(self, version: str, compiler: str) -> str:
        return ""

    def add_libraries(self, version: str, compiler: str, specs: list) -> str:
        return ""

    def add_time(self, version: str, compiler: str) -> str:
        return ""

    def add_workdir(self) -> str:
        return self.WORKDIR

    def copy_all(self) -> str:
        return self.COPY_ALL

    def add_compile(self, version: str, compiler: str, function_name: str, specs: dict) -> str:
        return ""

    def add_sleep_command(self) -> str:
        return self.SLEEP_COMMAND

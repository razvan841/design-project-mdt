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
import subprocess
import sys
from pathlib import Path
import os
from sys import platform
from sources.CustomException import *
from sources.LoggerConfig import logger

'''
Set whether to use the system shell.
This is normally true for windows machines and false for UNIX-based systems.
If you have issues running subprocesses, try force setting this constant to the opposite value.
'''
if platform != "win32":
    SHELL = False
else:
    SHELL = True

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

class Podman:
    def __init__(self):
        pass

    def process_to_lines(self, process: subprocess.CompletedProcess, output_name: str) -> list:
        '''
        Helper functions to process stdout and stderr pipes
        '''
        raw_output = getattr(process, output_name)
        raw_output = raw_output.splitlines()
        output = []
        for line in raw_output:
            output.append(line.decode(getattr(sys, output_name).encoding))
        return output

    def completed_process_to_lines(self, process: subprocess.CompletedProcess) -> dict:
        return {
            "stdout": self.process_to_lines(process, "stdout"),
            "stderr": self.process_to_lines(process, "stderr")
        }

    def check_for_errors(self, process: subprocess.CompletedProcess, exception: Exception) -> None:
        '''
        Function to check stderr pipe. There are some errors that it ignores, because they are just warnings
        '''
        stdout_lines = self.process_to_lines(process, "stdout")
        stderr_lines = self.process_to_lines(process, "stderr")
        stderr_lines = self.remove_metrics(stderr_lines)
        errors_to_ignore = ['warning', 'screen size is bogus', 'VM already running', 'Command being timed']
        errors = [line for line in stderr_lines if not any(ignore in line.lower() for ignore in errors_to_ignore)]
        if errors and not stdout_lines:
            error_text = "\n".join(errors)
            raise exception(f"Process encountered errors:\n{error_text}") from None

    def relative_to_vm_path(self, relative_path: str) -> str:
        '''
        Helper function to change windows relative path to unix path
        '''
        # get absolute file path
        path = os.path.abspath(relative_path)
        if platform != "linux" and platform != "linux2":
            # reinterpret path as posix
            path = Path(path).as_posix()
            # reinterpret disk name (e.g. "C:"" -> "c")
            path = path.replace(":", "")
            path = path[:1].lower() + path[1:]
            # add the /mnt/ vm directory
            path = "/mnt/" + path
        return path

    def print_process_output(self, process: subprocess.CompletedProcess) -> None:
        '''
        Helper function to print stdout and stderr pipes
        '''
        process_out = self.completed_process_to_lines(process)
        stdout = process_out['stdout']
        stderr = process_out['stderr']
        logger.debug(f'Podman: stdout: {stdout}')
        logger.stderr(f'Podman: stderr: {stderr}')

    def parse_time_output(self, stderr: str) -> dict:
        '''
        Helper function that parses output of 'time' metrics in dictionary format
        '''
        data = {}
        for line in stderr:
            line = line.strip()
            if ": " in line:
                key, value = line.split(": ", 1)
                key = key.replace("\t", "").strip()
                data[key] = value
        return data

    def remove_metrics(self, stderr: str) -> list:
        '''
        Helper function that removes output of 'time' from stderr
        '''
        result = []
        seen_first = False
        seen_last = False
        for line in stderr:
            if "\tCommand being timed:".lower() in line.lower():
                seen_first = True
            elif "\tExit status:".lower() in line.lower():
                seen_last = True
                continue
            if not seen_first or seen_last:
                result.append(line)
        return result

    def machine_exists(self, machine_name: str) -> bool:
        '''
        Check if podman machine is running
        '''
        machine = subprocess.run(["podman", "machine", "inspect", machine_name], capture_output=True, shell=SHELL)
        machine = self.completed_process_to_lines(machine)
        return machine['stdout'][0] != '[]'

    def clean_path(self, session_path: str = "sessions/"):
        '''
        Clean stray containers that may be present at program start
        '''
        session_path = os.path.join(parent_dir, session_path)
        sessions = os.listdir(session_path)
        for session in sessions:
            try:
                self.stop_container(f'container_{session}')
                self.remove_container(f'container_{session}')
                self.remove_image(f'image_{session}', f'image_tag_{session}')
            except ContainerStopException as e:
                logger.warning(f"Podman clean_path: error: {str(e)}")
            except ContainerRemoveException as e:
                logger.warning(f"Podman clean_path: error: {str(e)}")
            except ImageRemoveException as e:
                logger.warning(f"Podman clean_path: error: {str(e)}")
            finally:
                subpath = os.path.join(session_path, session)
                files = os.listdir(subpath)
                for file in files:
                    file_path = os.path.join(subpath, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(subpath)

    def init(self, machine_name: str = "podman-machine-default", session_path: str = "sessions/") -> None:
        '''
        Function to start the podman machine. Necessary for any container or image manipulation
        '''
        logger.info(f'Podman init: Starting podman machine: {machine_name}')
        if not self.machine_exists(machine_name):
            logger.info(f'Podman init: Machine {machine_name} does not exist; Init from scratch')
            machine_init = subprocess.run(["podman", "machine", "init"], capture_output=True, shell=SHELL)
            logger.info('Podman init: Init podman machine with output: ')
            self.print_process_output(machine_init)
            self.check_for_errors(machine_init, InitException)
        machine_start = subprocess.run(["podman", "machine", "start"], capture_output=True, shell=SHELL)
        logger.info('Podman init: Start podman machine with output:')
        self.print_process_output(machine_start)
        logger.info('Podman init: Cleaning stray containers...')
        self.clean_path(session_path)
        self.prune(machine_name)
        self.check_for_errors(machine_start, StartException)
        logger.info('Podman init: System initialized!')

    def prune(self, machine_name: str = "podman-machine-default") -> None:
        '''
        Prune hanging images
        '''
        logger.info(f'Podman prune: Pruning machine {machine_name}')
        prune = subprocess.run(['podman', 'image', 'prune', '-f'], capture_output=True, shell=SHELL)
        logger.info(f'Podman prune: Prune podman machine {machine_name} with output: ')
        self.print_process_output(prune)

    def stop(self, machine_name: str = "podman-machine-default") -> None:
        '''
        Function to stop the podman machine
        '''
        logger.info(f'Podman stop: Stopping podman machine: {machine_name}')
        machine_stop = subprocess.run(["podman", "machine", "stop", machine_name], capture_output=True, shell=SHELL)
        logger.info('Podman stop: Stop podman machine with output:')
        self.print_process_output(machine_stop)
        self.check_for_errors(machine_stop, StopException)

    def build_image(self, name: str, tag: str, mount_path: str = ".", file_path: str = "") -> None:
        '''
        Function to build image. It makes a syscall to podman to build the image using the file path
        '''
        if name != "":
            name = " -t " + name + ":" + tag + " "
        if file_path != "":
            file_path = " -f " + file_path + " "
        command = "podman build " + name + file_path + mount_path
        command = command.split()
        logger.info(f'Podman build_image: Creating image: {name}')
        image = subprocess.run(command, capture_output=True, shell=SHELL)
        logger.info('Podman build_image: Create image with output:')
        self.print_process_output(image)
        self.check_for_errors(image, ImageBuildException)

    def remove_image(self, name: str, tag: str) -> None:
        '''
        Remove an image from the list of podman images
        '''
        image_name = name + ":" + tag
        logger.info(f"Podman remove_image: Remove image: {image_name}")
        remove = subprocess.run(["podman", "image", "rm", image_name], capture_output=True, shell=SHELL)
        self.print_process_output(remove)
        self.check_for_errors(remove, ImageRemoveException)

    def run_image(self, image_name: str, tag: str, container_name: str) -> dict:
        '''
        Makes the container using an image
        '''
        image_name = image_name + ":" + tag
        logger.info(f'Podman run_image: Run image: {image_name}')
        run = subprocess.run(["podman", "run", "-d", "--name", container_name, image_name], capture_output=True, shell=SHELL)
        self.print_process_output(run)
        self.check_for_errors(run, ImageRunException)
        return self.completed_process_to_lines(run)

    def get_copy_command(self):
        '''
        If backend is running on a windows machine, we need to first ssh into the podman machine in order to copy files into a container.
        '''
        if platform != "linux" and platform != "linux2":
            return ["podman", "machine", "ssh"]
        else:
            return []

    def copy_to_container(self, file_path: str, container_name: str, dest: str = "/usr/src/app"):
        '''
        Copies a file to an already existing container. Important for reusing the container for another piece of code.
        '''
        logger.info(f'Podman copy_to_container: Copying file {file_path} to container {container_name}:{dest}')
        path = self.relative_to_vm_path(file_path)
        command = self.get_copy_command()
        command.append(f"podman cp {path} {container_name}:{dest}")
        # This literally failed for like 5 tries one time and then never again,
        # So it is now in a try block.
        # Seems to still work even if timeout expires?
        # schrodinger's bug fr
        # logger.critical(f"Before executing copy on container {container_name}")
        try:
            copy = subprocess.run(command, capture_output=True, shell=False, timeout=5)
            # logger.critical(f"After executing copy on container {container_name}")
            logger.info(f'Podman copy_to_container: Copy file {file_path} to container {container_name}:{dest} with output:')
            self.print_process_output(copy)
            self.check_for_errors(copy, CopyException)
        except Exception as e:
            logger.info(f'Podman copy_to_container: Timed out container {container_name}: {str(e)}')
            # logger.critical(f"After executing copy on container {container_name}")
            logger.info(f'Podman copy_to_container: Copy file {file_path} to container {container_name}:{dest} with output:')
            

    def exec_command(self, container_name: str, command: list, metrics: bool = False, timeout: int = 120) -> dict:
        '''
        Executes a command inside a podman container
        '''
        logger.info(f'Podman exec_command: Executing command {command} on container {container_name}')
        if metrics:
            command = ["/usr/bin/time", "-v"] + command
        command_split = ["podman", "exec", container_name] + command
        exec_output = subprocess.run(command_split, capture_output=True, shell=SHELL, timeout=timeout)
        logger.info(f'Podman exec_command: Executed command {command} on container {container_name} with output:')
        self.print_process_output(exec_output)
        output = self.completed_process_to_lines(exec_output)
        if metrics:
            output['metrics'] = self.parse_time_output(output['stderr'])
            output['stderr'] = self.remove_metrics(output['stderr'])
        self.check_for_errors(exec_output, ExecutionException)
        return output

    def stop_container(self, container_name: str) -> None:
        '''
        Stops a podman container
        '''
        logger.info(f'Podman stop_container: Stopping container {container_name}')
        stop_output = subprocess.run(["podman", "stop", "-t", "0", container_name], capture_output=True, shell=SHELL)
        logger.info(f'Podman stop_container: Stop container {container_name} with output:')
        self.print_process_output(stop_output)
        self.check_for_errors(stop_output, ContainerStopException)

    def remove_container(self, container_name: str) -> None:
        '''
        Removes a container
        '''
        logger.info(f'Podman remove_container: Removing container {container_name}')
        remove_output = subprocess.run(["podman", "rm", container_name], capture_output=True, shell=SHELL)
        logger.info(f'Podman remove_container: Remove container {container_name} with output:')
        self.print_process_output(remove_output)
        self.check_for_errors(remove_output, ContainerRemoveException)

podman = Podman()
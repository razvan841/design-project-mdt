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
import sys, time, threading, os, re

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.Container import Container, format_output
from queue import Queue
from sources.CustomException import *
from sources.LoggerConfig import logger
from sources.DockerMaker import EXECUTION_PATH

MAX_CONTAINERS = 4

index_lock = threading.RLock()
class ContainerManager:
    '''
    Class to handle containers
    '''
    def __init__(self, container_class: Container = Container):
        self.containers = {}
        self.last_index = 0
        self.container_class = container_class
        self.container_count = 0

    def add_container(self, metadata: dict, run_as_is: bool = False) -> int:
        '''
        function to create new container. we store in the container dict some metadata so we can check
        later if a user code can be put in an already existing container
        '''

        timestamp = time.time()
        if self.container_count >= MAX_CONTAINERS:
            index_lock.release()
            raise RuntimeError("Maximum number of containers reached")

        index = self.last_index
        self.last_index += 1
        self.container_count+=1

        index_lock.release()

        try:
            container = self.container_class(metadata = metadata, index = index, run_as_is = run_as_is)
            environment = self.get_environment(metadata)
        except InitContainerException as e:
            with index_lock:
                self.remove_folder(index)
                self.container_count -=1
            raise InitContainerException(e)
        with index_lock:
            self.containers[index] = (container, environment, timestamp)

        return index

    def remove_folder(self, index : int) -> None:
        path = os.path.join(EXECUTION_PATH,f"{index}")
        try:
            files = os.listdir(path)
            for file in files:
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(path)
        except Exception as e:
            raise OSError("Failed to remove folder")


    def execute(self, data: dict, inputs: list, timeout: int, run_as_is: bool = False) -> list:
        '''
        Function that executes a piece of code using its metadata and a list of inputs.
        It checks if there are any available containers. if yes, it puts the code and metadata in the available container.
        if no, it tries to find the oldest
        container that is not being used, it removes it and creates a new container to run the code in.
        '''
        environment = self.get_environment(data)
        language = environment.get("language", "")
        container_to_remove = None
        with index_lock:
            index = self.check_containers(environment)
        outputs = []
        i = 0
        try:
            # C# and Rust can't make use of container recycling
            if index != -1 and language != "cs" and language != "c#" and language != "rust":
                container, _, __ = self.containers[index]
                container.set_metadata(data)
                container.set_run_as_is(run_as_is)
                container.change_code()
            else:
                index_lock.acquire()
                logger.debug(f"Container Manager execute: Found {self.container_count}")

                if self.container_count >= MAX_CONTAINERS:
                    container_to_remove = self.get_oldest_container()
                    if container_to_remove is not None:
                        container_to_remove.terminate()

                index = self.add_container(metadata=data, run_as_is=run_as_is)
                container, _, __ = self.containers[index]
                container.compile_code()
            while i < len(inputs):
                input = inputs[i]
                output = container.run_code(input, timeout)
                output['input'] = input
                outputs.append(output)
                i += 1
            self.containers[index] = (container, environment, time.time())
            return outputs

        except NoContainerException as e:
            raise NoContainerException(e)
        except Exception as e:
            if isinstance(e, ContainerFileCommunicationException):
                with index_lock:
                    self.containers.pop(index)
                    container.terminate()
                    self.container_count -=1
            error_case = format_output(stderr=str(e))
            error_case['input'] = inputs[i]
            i += 1
            outputs.append(error_case)
            while len(outputs) < len(inputs):
                error_case = format_output(stderr='Prior execution failed')
                error_case['input'] = inputs[i]
                i += 1
                outputs.append(error_case)
            logger.debug(f"Container Manager execute: Prior execution failed")
            return outputs

    def execute_parallel(self, options: list, inputs: list, timeout: int) -> list:
        '''
        Function to be called by the server. It calls the execute function on separate threads
        '''
        threads = []
        results = []

        job_queue = Queue()
        for data in options:
            job_queue.put((data, inputs))

        def worker(job_queue: Queue):
            while not job_queue.empty():
                data, inputs = job_queue.get()
                run_as_is = data.get("run_as_is", False)
                try:
                    result = self.execute(data, inputs, timeout, run_as_is)
                    results.append({data['cell_id']: result})
                except NoContainerException:
                    job_queue.put((data, inputs))
                except Exception as e:
                    results.append({data['cell_id']: [format_output(stderr=str(e))]})

        for _ in range(MAX_CONTAINERS):
            thread = threading.Thread(target=worker, args=[job_queue])
            threads.append(thread)
            thread.setDaemon(True)
            thread.start()


        for thread in threads:
            thread.join()

        return results

    def check_containers(self, environment: dict) -> int:
        '''
        Function to check if there is an available container with correct environment variables
        '''
        for index, (container, env, _) in self.containers.items():
            if(env == environment and container.is_available()):
                logger.info(f"Container Manager check_containers: Found available container with index: {index}")
                # if found an available container, set it to false to avoid race conditions.
                container.set_available(False)
                return index
        return -1

    def get_environment(self, metadata: dict) -> dict:
        '''
        helper function to extract environment data relevant for the container from data
        '''
        language = metadata['language']
        version = metadata['version']
        compiler = metadata['compiler']
        specs = metadata['specs']

        return {
            "language" : language,
            "version" : version,
            "compiler" : compiler,
            "specs" : specs
        }

    def check_container_available(self, index:int) -> bool:
        '''
        Helper function to check if a specific container is available
        '''
        container = self.containers.get(index)[0]
        return container.is_available()

    def get_oldest_container(self) -> None:
        '''
        Helper function to find the oldest available container and remove it so there is enough space for a new container
        '''
        max_time = time.time()
        index_to_remove = -1
        for index, (container, _, timestamp) in self.containers.items():
            if timestamp < max_time and self.check_container_available(index):
                max_time = timestamp
                index_to_remove = index

        if(index_to_remove == -1):
            raise NoContainerException("No container available to be removed")
        container, _ , __ = self.containers.pop(index_to_remove)
        container.set_available(False)
        self.container_count-=1
        return container

    def purge(self) -> None:
        '''
        Remove all containers
        '''
        for index in self.containers.keys():
            container = self.containers.get(index)[0]
            container.terminate()
        self.containers = {}
        self.container_count=0

    def calculate_status(self) -> float:
        '''
        Function to approximate completion rate of execution
        Looks at the exec.log and looks at logs that show what stages were completed
        '''
        status  = 0
        filename = 'exec.log'
        with open(filename, 'r') as file:
            content = file.read()

        code_cells_match = re.search(r"Code cells:\s*(\d+)", content)
        total_test_cases_match = re.search(r"Total test cases:\s*(\d+)", content)

        code_cells = int(code_cells_match.group(1)) if code_cells_match else None
        total_test_cases = int(total_test_cases_match.group(1)) if total_test_cases_match else None

        dockers_done = content.count('Dockerfile')
        status += 0.1 * dockers_done / code_cells
        injects_done = content.count('Inject')
        status += 0.1 * injects_done / code_cells
        builds_done = content.count('Build')
        status += 0.25 * builds_done / code_cells
        runs_done = content.count('Run image')
        status += 0.1 * runs_done / code_cells
        tests_done = content.count('Test')
        status += 0.45 * tests_done / code_cells / total_test_cases
        return status


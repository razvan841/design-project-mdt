import time
import unittest,os,sys, subprocess,threading
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from pytest import MonkeyPatch

from sources.Podman import podman
from sources.CustomException import *
from sources.LoggerConfig import logger
from sources.Container import Container
from sources.ContainerManager import ContainerManager, index_lock, MAX_CONTAINERS

class CM_Container(unittest.TestCase):
    '''
    Class for testing Manager - Container Communication
    The test should be run with a running podman machine.
    Do not start any other application that might start containers while running the test
    '''

    class MockContainerManager(ContainerManager):
        '''
        Mock class to overwrite index. Neccesary if any containers are already running.
        '''
        def __init__(self, container_class = Container):
            self.containers = {}
            self.last_index = 99999
            self.container_class = container_class
            self.container_count = 0



    def setUp(self):
        self.manager = self.MockContainerManager()
        self.initial_index = self.manager.last_index
        self.metadata_0 = {
            "cell_id":0,
            "code":"def mul(a, b):\n\treturn a + b\n",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "float"
                ],
                "return":"float"
            },
            "language":"Python",
            "version":"3.11",
            "compiler":"",
            "specs":{

            },
            "run_as_is":False
        }
        self.metadata_1 = {
            "cell_id":0,
            "code":"def mul(a, b):\n\treturn a + b\n",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "float"
                ],
                "return":"float"
            },
            "language":"Python",
            "version":"3.12",
            "compiler":"",
            "specs":{

            },
            "run_as_is":False
        }
        self.metadata_2 = {
            "cell_id":0,
            "code":"def mul(a, b):\n\treturn a + b\n",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "float"
                ],
                "return":"float"
            },
            "language":"Python",
            "version":"3.12",
            "compiler":"",
            "specs":{

            },
            "run_as_is":False
        }
        self.metadata_bad = {
            "cell_id":0,
            "code":"def mul(a, b):\n\tretu a+b\n",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "float"
                ],
                "return":"float"
            },
            "language":"Python",
            "version":"3.12",
            "compiler":"",
            "specs":{

            },
            "run_as_is":False
        }

        return super().setUp()

    def remove_test_sessions(self,path):
        try:
            files = os.listdir(path)
            for file in files:
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(path)
        except Exception as e:
            pass


    def tearDown(self):
        for i in range (0,5):
            index = i + self.initial_index
            path = os.path.join("../sessions", f"{index}")
            self.remove_test_sessions(path=path)
            subprocess.run(["podman", "container", "rm", f"container_{index}" ,"-f", "-t", "0"], capture_output=True)
            subprocess.run(["podman", "image", "rm", f"image_{index}:image_tag_{index}" ], capture_output=True)


    def test_add_container(self):
        index_lock.acquire()
        self.manager.add_container(self.metadata_0)
        assert self.manager.container_count == 1
        assert self.manager.last_index == self.initial_index +1
        assert len(self.manager.containers) == 1


    def test_add_container_exception(self):
        subprocess.run(["podman","machine","stop"])
        with self.assertRaises(InitContainerException):
            index_lock.acquire()
            self.manager.add_container(self.metadata_0)
        subprocess.run(["podman","machine","start"],capture_output=True)
        self.manager.container_count = MAX_CONTAINERS
        with self.assertRaises(RuntimeError):
            index_lock.acquire()
            self.manager.add_container(self.metadata_0)


    def test_execute(self):

        #Check if container is correctly created with new enviroment
        output = self.manager.execute(self.metadata_0,[["2","2"]],timeout=60)
        assert "4" in output[0]["stdout"][0]
        assert self.manager.container_count == 1
        containers_first_run = subprocess.run(["podman","container","ls","-a"],capture_output=True,text=True).stdout.count('\n')

        #Check if no new container is created for same metadata
        output = self.manager.execute(self.metadata_0,[['3','3'],['4','4']],timeout=60)
        assert "6" in output[0]["stdout"][0]
        containers_second_run = subprocess.run(["podman","container","ls","-a"],capture_output=True,text=True).stdout.count('\n')
        assert self.manager.container_count == 1
        print(output)
        assert "8" in output[1]["stdout"][0]

        #Check if there are 2 outputs
        assert len(output) == 2

        #Check if no new containers are created in Podman system
        assert containers_first_run == containers_second_run

        #Check if new container is created for different metadata
        output = self.manager.execute(self.metadata_1,[["2","2"]],timeout=60)
        containers_different_run = subprocess.run(["podman","container","ls","-a"],capture_output=True,text=True).stdout.count('\n')
        assert containers_different_run > containers_second_run
        assert self.manager.container_count == 2

        #Check number of containers will not go above MAX_CONTAINERS
        self.manager.container_count = MAX_CONTAINERS
        output = self.manager.execute(self.metadata_2,[["2","2"]],timeout=60)
        assert self.manager.container_count == 4


    def test_execute_bad_code(self):

        output = self.manager.execute(self.metadata_bad,[["2","2"]],timeout=60)
        assert "error" in output[0]["stderr"][0]

    def test_execute_parallel(self):
        options = [self.metadata_0,self.metadata_1]
        results = self.manager.execute_parallel(options,inputs=[["2","2"]],timeout=60)
        assert len(results) == 2



    def test_check_containers(self):
        index_lock.acquire()
        index_0 = self.manager.add_container(self.metadata_0)
        env_0 = self.manager.get_environment(self.metadata_0)
        checked_index_0 = self.manager.check_containers(env_0)
        assert index_0 == checked_index_0
        container = self.manager.containers[index_0][0]
        assert container.is_available() == False
        env_1 = self.manager.get_environment(self.metadata_1)
        checked_index_1 = self.manager.check_containers(env_1)
        assert -1 == checked_index_1

    def test_get_oldest_containers(self):
        index_lock.acquire()
        index_0 = self.manager.add_container(self.metadata_0)
        index_lock.acquire()
        index_1 = self.manager.add_container(self.metadata_1)
        assert self.manager.container_count == 2
        assert len(self.manager.containers) == 2

        first_container = self.manager.containers[index_0][0]
        oldest_container = self.manager.get_oldest_container()
        assert oldest_container == first_container
        assert self.manager.container_count == 1
        assert len(self.manager.containers) == 1

    def test_get_oldest_container_exception(self):
        index_lock.acquire()
        index_0 = self.manager.add_container(self.metadata_0)
        container_0 = self.manager.containers[index_0][0]
        container_0.set_available(False)
        with self.assertRaises(NoContainerException):
            self.manager.get_oldest_container()

    def test_purge(self):
        index_lock.acquire()
        index_0 = self.manager.add_container(self.metadata_0)
        index_lock.acquire()
        index_1 = self.manager.add_container(self.metadata_1)
        self.manager.purge()
        containers = subprocess.run(["podman","container","ls","-a"],capture_output=True,text=True).stdout
        images = subprocess.run(["podman","image","ls","-a"], capture_output=True,text=True).stdout
        assert f"container_{index_0}" not in containers
        assert f"container_{index_1}" not in containers
        assert f"image_{index_0}" not in images
        assert f"image_{index_1}" not in images
        path_0 = os.path.join("../sessions",f"{index_0}")
        with self.assertRaises(FileNotFoundError):
            files = os.listdir(path_0)

        path_1 = os.path.join("../sessions",f"{index_1}")
        with self.assertRaises(FileNotFoundError):
            files = os.listdir(path_1)





if __name__ == "__main__":
    unittest.main()


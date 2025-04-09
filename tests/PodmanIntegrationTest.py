import time
import unittest,os,sys, subprocess
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from pytest import MonkeyPatch

from sources.Podman import podman, Podman
from sources.CustomException import *
from sources.LoggerConfig import logger

class PodmanIntegrationTest(unittest.TestCase):
    '''
    Class to test integration of the podman system and Podman.py interface.
    The test should be run with a running podman machine.
    Do not start any other application that might start containers while running the test
    '''

    class MockPodman(Podman) :
        def __init__(self):
            super().__init__()

        def init(self, init:bool, machine_name: str = "podman-machine-default", session_path: str = "../sessions/") -> None:
            '''
            Function to start the podman machine. Necessary for any container or image manipulation
            '''
            logger.info(f'Podman init: Starting podman machine: {machine_name}')
            if init:
                logger.info(f'Podman init: Machine {machine_name} does not exist; Init from scratch')
                machine_init = subprocess.run(["podman.cmd", "machine", "init"], capture_output=True)
                logger.info('Podman init: Init podman machine with output: ')
                self.print_process_output(machine_init)
                self.check_for_errors(machine_init, InitException)
            else:
                machine_start = subprocess.run(["podman.cmd", "machine", "start"], capture_output=True)
                logger.info('Podman init: Start podman machine with output:')
                self.print_process_output(machine_start)
                logger.info('Podman init: Cleaning stray containers...')
                #self.clean_path(session_path)
                self.check_for_errors(machine_start, StartException)
                logger.info('Podman init: System initialized!')


    def setUp(self):
        self.real_machine_name = "podman-machine-default"
        self.fake_machine_name = "podman-fake-machine"
        self.correct_image_path = os.path.join("test_sessions","correct_docker_image")
        self.bad_image_path = os.path.join("test,sessions","bad_docker_image")
        self.path_to_delete = "..test/path_to_delete/"
        self.mock_podman = self.MockPodman()
        self.monkeypatch = MonkeyPatch()
        self.image_name = "image_test"
        self.image_tag = "image_tag"
        self.container_name = "test_container"
        return super().setUp()

    def tearDown(self):
        podman.init()
        subprocess.run(["podman","stop","-t","0",self.container_name])
        subprocess.run(["podman","container","rm","-f",self.container_name])
        subprocess.run(["podman","image","rm", f"{self.image_name}:{self.image_tag}"])
        return super().tearDown()

    def test_machine_exists_real_machine(self):
        self.assertTrue(podman.machine_exists(self.real_machine_name))

    def test_machine_exists_fake_machine(self):
        self.assertFalse(podman.machine_exists(self.fake_machine_name))

    def test_init_InitException(self):

        custom_podman_dir = os.path.abspath("fakebin")
        original_path = os.environ.get("PATH","")
        new_path = custom_podman_dir + os.pathsep + original_path
        self.monkeypatch.setenv("PATH",new_path)
        with self.assertRaises(InitException):
            self.mock_podman.init(init=True)


    def test_init_StartException(self):

        custom_podman_dir = os.path.abspath("fakebin")
        original_path = os.environ.get("PATH","")
        new_path = custom_podman_dir + os.pathsep + original_path
        self.monkeypatch.setenv("PATH",new_path)
        with self.assertRaises(StartException):
            self.mock_podman.init(init=False)

    def test_stop(self):

        try:
            podman.stop()
        except Exception:
            self.fail("podman.stop should not have thrown exception")

    def test_stop_exception(self):

        with self.assertRaises(StopException):
            podman.stop(self.fake_machine_name)

    def test_build_image(self):
        podman.init()
        podman.build_image(name= self.image_name, tag=self.image_tag, mount_path=self.correct_image_path)
        images = subprocess.run(["podman", "image" , "ls", "-a"], capture_output=True, text=True)
        assert self.image_name in images.stdout.lower()

    def test_build_image_exception(self):

        with self.assertRaises(ImageBuildException):
            podman.build_image(name=self.image_name, tag=self.image_tag, mount_path=self.bad_image_path)

    def test_remove_image(self):
        subprocess.run(["podman","build","-t",f"{self.image_name}:{self.image_tag}",self.correct_image_path])
        podman.remove_image(name=self.image_name,tag=self.image_tag)
        image_list = subprocess.run("podman image ls -a", capture_output=True, text= True)
        self.assertTrue(self.image_name not in image_list.stdout)

    def test_remove_image_exception(self):

        with self.assertRaises(ImageRemoveException):
            podman.remove_image(name = self.image_name, tag=self.image_tag)

    def test_run_image(self):

        subprocess.run(["podman","build","-t",f"{self.image_name}:{self.image_tag}",self.correct_image_path])
        output = podman.run_image(image_name=self.image_name,tag=self.image_tag,container_name=self.container_name)
        print(output)
        assert [] == output.get("stderr")

    def test_run_image_exception(self):

        with self.assertRaises(ImageRunException):
            podman.run_image(image_name=self.image_name,tag=self.image_tag,container_name=self.container_name)

    def test_copy_to_container(self):

        subprocess.run(["podman","build","-t",f"{self.image_name}:{self.image_tag}",self.correct_image_path])
        print("built imag")
        podman.run_image(self.image_name,self.image_tag,self.container_name)
        print("ran image")
        test_file_path = os.path.join("test_sessions", "test_files")
        podman.copy_to_container(test_file_path,self.container_name)
        print("copied to container")
        output = subprocess.run([ "podman", "exec", "-it", f"{self.container_name}", "ls"], capture_output=True,text=True)
        assert "test" in output.stdout

    def test_copy_to_container_exception(self):

        with self.assertRaises(CopyException):
            podman.copy_to_container(self.bad_image_path,self.container_name)

    def test_exec_comand(self):

        subprocess.run(["podman","build","-t",f"{self.image_name}:{self.image_tag}",self.correct_image_path])
        podman.run_image(self.image_name,self.image_tag,self.container_name)
        output = podman.exec_command(self.container_name,["java", "addTwoNumbers_injected", "1", "2"])
        assert [] == output.get("stderr")

    def test_exec_command_exception(self):

        with self.assertRaises(ExecutionException):
            podman.exec_command(self.container_name,["bad command"])

    def test_stop_container(self):

        subprocess.run(["podman","build","-t",f"{self.image_name}:{self.image_tag}",self.correct_image_path])
        podman.run_image(self.image_name,self.image_tag,self.container_name)
        podman.stop_container(container_name=self.container_name)
        output = subprocess.run(["podman", "container", "ls" ,"-a"], capture_output=True, text=True)
        assert "Up" not in output.stdout

    def test_stop_container_exception(self):

        with self.assertRaises(ContainerStopException):
            podman.stop_container("none")

    def test_remove_container(self):

        subprocess.run(["podman","build","-t",f"{self.image_name}:{self.image_tag}",self.correct_image_path])
        podman.run_image(self.image_name,self.image_tag,self.container_name)
        podman.stop_container(self.container_name)
        podman.remove_container(self.container_name)
        output = subprocess.run(["podman", "container", "ls" ,"-a"], capture_output=True, text=True)
        assert self.container_name not in output.stdout

    def test_remove_container_exception(self):
        with self.assertRaises(ContainerRemoveException):
            podman.remove_container(self.container_name)








if __name__ == "__main__":
    unittest.main()
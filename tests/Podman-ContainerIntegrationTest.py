import time
import unittest,os,sys, subprocess
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from pytest import MonkeyPatch

from sources.Podman import podman
from sources.CustomException import *
from sources.LoggerConfig import logger
from sources.Container import Container

class Podman_ContainerIntTest(unittest.TestCase):

    '''
    Class to test Integration of Container - Podman components.
    The test should be run with a running podman machine.
    Do not start any other application that might start containers while running the test
    '''

    def setUp(self):
        self.metadata = {
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
        self.metadata_sum = {
            "cell_id":0,
            "code":"def sum(a, b):\n\treturn a + b\n",
            "signature":{
                "name":"sum",
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
        self.bad_metadata ={
            "cell_id":0,
            "code": "public static float mul(float a, floatb){\n\treturn a+b;}",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "float"
                ],
                "return":"float"
            },
            "language":"java",
            "version":"21",
            "compiler":"amazoncorretto",
            "specs":{

            },
            "run_as_is":False
        }

        self.metadata_run_as_is = {
            "cell_id":0,
            "code": "import time\ndef sum(a, b):\n\treturn a + b\n\nimport sys\ndef main():\n\ta = int(sys.argv[1])\n\tb = int(sys.argv[2])\n\tresult = sum(a, b)\n\tprint(result)\nif __name__ == '__main__':\n\tmain()",
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
            "run_as_is":True
        }
        self.bad_run_as_is = self.metadata_run_as_is = {
            "cell_id":0,
            "code": "import tinee\ndef sum(a, b):\n\treturn a + b\n\nimport sys\ndef main():\n\ta = int(sys.argv[1])\n\tb = int(sys.argv[2])\n\tresult = sum(a, b)\n\tprint(result)\nif __name__ == '__main__':\n\tmain()",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "floar"
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

        self.metadata_java = {
            "cell_id":0,
            "code": "public static float mul(float a, float b){\n\treturn a+b;}",
            "signature":{
                "name":"mul",
                "args":[
                    "float",
                    "float"
                ],
                "return":"float"
            },
            "language":"java",
            "version":"21",
            "compiler":"amazoncorretto",
            "specs":{

            },
            "run_as_is":False
        }
        self.index = 999999999
        return super().setUp()


    def tearDown(self):
        subprocess.run(["podman", "container", "rm", f"container_{self.index}" ,"-f", "-t", "0"], capture_output=True)
        subprocess.run(["podman", "image", "rm", f"image_{self.index}:image_tag_{self.index}" ], capture_output=True)
        path = os.path.join("../sessions", f"{self.index}")
        try:
            files = os.listdir(path)
            for file in files:
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(path)
        except Exception as e:
            pass
        return super().tearDown()


    def test_init(self):
        container = Container(metadata=self.metadata,index=self.index)
        images = subprocess.run(["podman","image", "ls", "-a"], capture_output=True,text=True).stdout
        containers = subprocess.run(["podman","container", "ls", "-a"],capture_output=True,text=True).stdout
        files = subprocess.run(["podman", "exec", "-it", f"container_{self.index}", "ls"],capture_output=True, text=True).stdout
        self.assertTrue("Dockerfile" in files)
        self.assertTrue(f"image_{self.index}" in images)
        self.assertTrue(f"container_{self.index}" in containers)


    def test_init_exceptions(self):
        Container(self.metadata, self.index)
        with self.assertRaises(InitContainerException):
            Container(self.metadata, self.index)


    def test_init_run_as_is(self):
        Container(metadata=self.metadata_run_as_is,index=self.index, run_as_is=True)
        images = subprocess.run(["podman","image", "ls", "-a"], capture_output=True,text=True).stdout
        containers = subprocess.run(["podman","container", "ls", "-a"],capture_output=True,text=True).stdout
        files = subprocess.run(["podman", "exec", "-it", f"container_{self.index}", "ls"],capture_output=True, text=True).stdout
        self.assertTrue("Dockerfile" in files)
        self.assertTrue(f"image_{self.index}" in images)
        self.assertTrue(f"container_{self.index}" in containers)


    def test_init_run_as_is_exception(self):
        with self.assertRaises(InitContainerException):
            Container(metadata=self.bad_run_as_is, index=self.index)

    def test_run_code(self):
        container = Container(metadata=self.metadata,index=self.index)
        output = container.run_code(["2","2"])
        assert "4.0" in output['stdout']

    def test_run_code_bad_input(self):
        container = Container(metadata=self.metadata,index=self.index)
        with self.assertRaises(RunCodeException):
            container.run_code([2,2])

    def test_compile_code(self):
        container = Container(metadata=self.metadata_java,index=self.index)
        output = container.compile_code()
        assert [] == output.get("stderr")
        files  = subprocess.run(["podman","exec","-it",f"container_{self.index}", "ls"],capture_output=True,text=True).stdout
        assert ".class" in files

    def test_compile_code_exception(self):
        container = Container(metadata=self.metadata_java,index=self.index)
        subprocess.run(["podman","container","stop",f"container_{self.index}"])
        with self.assertRaises(CompileCodeException):
            container.compile_code()


    def test_terminate_container(self):
        container = Container(metadata=self.metadata,index=self.index)
        container.terminate()
        images = subprocess.run(["podman","image", "ls", "-a"], capture_output=True,text=True).stdout
        containers = subprocess.run(["podman","container", "ls", "-a"],capture_output=True,text=True).stdout
        assert f"image_{self.index}" not in images
        assert f"container_{self.index}" not in containers



    def test_terminate_exception(self):
        container = Container(metadata=self.metadata,index=self.index)
        subprocess.run(["podman", "container", "rm", f"container_{self.index}" ,"-f", "-t", "0"])
        subprocess.run(["podman", "image", "rm", f"image_{self.index}:image_tag_{self.index}" ])
        with self.assertRaises(TerminateException):
            container.terminate()

    def test_clear(self):
        container = Container(metadata=self.metadata,index=self.index)
        container.clear()
        output = subprocess.run(["podman","exec","-it",f"container_{self.index}", "ls"],capture_output=True,text=True).stdout
        assert "Dockerfile" not in output


    def test_clear_exception(self):
        container = Container(metadata=self.metadata,index=self.index)
        subprocess.run(["podman", "container", "rm", f"container_{self.index}" ,"-f", "-t", "0"], capture_output=True)
        with self.assertRaises(ClearException):
            container.clear()


    def test_change_code(self):
        container = Container(metadata=self.metadata,index=self.index)
        container.set_metadata(self.metadata_sum)
        container.change_code()
        files = subprocess.run(["podman", "exec", "-it", f"container_{self.index}", "ls"],capture_output=True, text=True).stdout
        assert "sum" in files

    def test_change_code_exception(self):
        container = Container(metadata=self.metadata,index=self.index)
        subprocess.run(["podman", "container", "rm", f"container_{self.index}" ,"-f", "-t", "0"])
        with self.assertRaises(ContainerFileCommunicationException):
            container.change_code()
        container = Container(metadata=self.metadata_java,index=self.index)
        container.set_metadata(self.bad_metadata)
        with self.assertRaises(ChangeCodeException):
            container.change_code()


    def test_upload_code(self):
        container = Container(metadata=self.metadata,index=self.index)
        output = subprocess.run(["podman","exec","-t",f'container_{self.index}',"ls"],capture_output=True,text=True).stdout
        output = output.split(" ")
        for file in output:
            subprocess.run(["podman","exec","-t",f'container_{self.index}',"rm", file],capture_output=True,text=True)

        container.upload_code()
        files = subprocess.run(["podman", "exec", "-t", f"container_{self.index}", "ls"],capture_output=True, text=True).stdout
        assert "Dockerfile" in files







if __name__ == "__main__":
    unittest.main()
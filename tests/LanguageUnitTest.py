import os,sys
import unittest
from unittest.mock import MagicMock,patch
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.Injector import Injector
from sources.DockerMaker import DockerMaker
from sources.languages.Language import Language

class TestLanguage(unittest.TestCase):
    #override the instantiations of Injector and Dockermacker with mock objects in the constructor
    def setUp(self):
        #make the language object
        self.language = Language()
        #mock the other 2
        self.language.injector = MagicMock()
        self.language.docker_maker = MagicMock()
        #give mock available versions
        self.available_versions = ['1,2','3.5','5.6']
        self.available_compilers = ['gcc','clang']
        self.helper_files = []
        self.extention = ".txt"

    def test_generate_run_command(self):
        with patch.object(self.language,'generate_run_command',wraps = self.language.generate_run_command) as mock_generate_run_command:
            command = self.language.generate_run_command("function",[5,6])
            mock_generate_run_command.assert_called_with("function",[5,6])
            self.assertEqual(command,[])

    def test_generate_compile_command(self):
        with patch.object(self.language,'generate_compile_command',wraps = self.language.generate_compile_command) as mock_generate_compile_command:
            compile_command = self.language.generate_compile_command("function","gcc")
            mock_generate_compile_command.assert_called_with("function","gcc")
            self.assertEqual(compile_command,[])

    def test_inject(self):
        source_path = "source.py"
        destination_path = "destination.py"
        signature = {
                    "name": "sum_numbers",
                    "args":{
                        "a": "int",
                        "b": "int"
                    }}
        
        #call the inject funciton
        self.language.inject(source_path=source_path,destination_path=destination_path,signature=signature)
        #check that the injector object was called with the right arguments
        self.language.injector.inject.assert_called_once_with(source_path,destination_path,signature)


    def test_generate_dockerfile(self):
        version = "3.10"
        compiler = ""
        function_name = "funciton"
        specs = {"libraries":"numpy"}
        index = 1

        #call the generate_dockerfile funciton
        self.language.generate_dockerfile(version=version,compiler=compiler,function_name=function_name,specs=specs,index=index)
        #check that the docker_maker's function was called with the right arguments
        self.language.docker_maker.generate_dockerfile.assert_called_once_with(version,compiler,function_name,specs,index)

    def test_get_available_versions(self):
        result = self.available_versions
        self.assertEqual(['1,2','3.5','5.6'], result)
    
    def test_available_compilers(self):
        result = self.available_compilers
        self.assertEqual(['gcc','clang'],result)

    def test_get_extension(self):
        result = self.extention
        self.assertEqual('.txt',result)
   
if __name__ == "__main__":
    unittest.main()

import os,sys,shutil
import unittest
from unittest.mock import MagicMock,patch
import tempfile
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.DockerMaker import EXECUTION_PATH
from sources.Podman import Podman, podman
from sources.CustomException import *
from sources.LoggerConfig import logger
from sources.LanguageFactory import LanguageFactory
from sources.Container import Container

class TestContainer(unittest.TestCase):
    def setUp(self):
        #make a temporary directory as EXECUTION_PATH
        self.temp_dir = tempfile.TemporaryDirectory()
        #path EXECUTION_PATH to get the mock temporary directory
        self.exec_patch_patcher = patch('sources.Container.EXECUTION_PATH',new = self.temp_dir.name)
        self.exec_patch_patcher.start()
        #dummy metadata for testing
        self.metadata = {
                "cell_id":1,
                "code": "def sum_numbers(a, b):\n\treturn a + b\n",
                "signature": {
                    "name": "sum_numbers",
                    "args":{
                        "a": "int",
                        "b": "int"
                    },
                    "return": "int"
                },
                "language": "Python",
                "version": "3.10",
                "compiler":"",
                "specs": {"libraries":"numpy"}
                        }
        self.available = True
        self.index = 1
        self.run_as_is = False
        #crate mocks of both the podman and language instances
        self.podman = MagicMock()
        self.language= MagicMock()
        #mock all the methods that the language instance will use and will be called 
        #testing with no helper files yet
        self.language.helper_files = []
        self.language.get_extension.return_value = "py"
        self.language.generate_dockerfile.return_value = True
        self.language.inject.return_value = None
        self.language.generate_run_command.return_value = "run_command"
        self.language.generate_compile_command.return_value = "compile_command"
        self.language.check_signature.return_value = self.metadata['signature']
        #patch the Language factory so it gets the mocked Language
        self.language_factory_patcher = patch('sources.LanguageFactory.LanguageFactory.get_language',return_value = self.language)
        self.language_factory = self.language_factory_patcher.start()
        #mock all the methods that the podman instance will use and will be called
        self.podman.build_image.return_value = None
        self.podman.run_image.return_value = None
        self.podman.exec_command.return_value = {"stdout" : ["output"], "stderr":[]}
        self.podman.stop_container.return_value = None
        self.podman.remove_container.return_value = None
        self.podman.remove_image.return_value = None
        self.podman.copy_to_container.return_value = None 
        #create a container object 
        self.container = Container(self.metadata,self.index,self.podman, run_as_is=False)
        

    def tearDown(self):
        self.exec_patch_patcher.stop()
        self.language_factory_patcher.stop()
        self.temp_dir.cleanup()

    def test_constructor(self):
        '''
        Tests that the constructor of the class Container behaves as wanted, namely, if  it calls create_dockerfile,
        inject, build_image and run_image as it should, and if it sets the mounting path accordingly
        '''
        #check that the mounting path is correct
        true_mounting_path = os.path.join(self.temp_dir.name,f'{self.index}')
        self.assertEqual(true_mounting_path,self.container.mounting_path)

        #check that generate_dockerfile was called with the correct arguments
        self.language.generate_dockerfile.assert_called_once_with(version = self.metadata['version'],compiler = self.metadata['compiler'], function_name = self.metadata['signature']['name'],specs = self.metadata['specs'],index = self.index)

        #check that the inject function was called with the right arguments
        self.language.inject.assert_called_once()
        args, kwargs = self.language.generate_dockerfile.call_args
        #check that the first argument which is file_path containts the funciton name as it should
        self.assertIn(self.metadata['signature']['name'],kwargs['function_name'])
        self.assertIn(self.metadata['signature']['name'],kwargs['function_name'])
       
        #check that the build_image command was called
        self.podman.build_image.assert_called_once_with(f'image_{self.index}', f'image_tag_{self.index}',mount_path=true_mounting_path)

        #check that the run_image command was called
        self.podman.run_image.assert_called_once_with(image_name=f'image_{self.index}',tag=f'image_tag_{self.index}',container_name=f'container_{self.index}')


    def test_constructor_error(self):
        #set inject to raise an error
        self.language.inject.side_effect = Exception("constructor error")
        with self.assertRaises(InitContainerException) as context:
            Container(self.metadata,self.index,self.podman,run_as_is=False)
        #check if the exeption is thrown
        self.assertIn("constructor error",str(context.exception))

    def test_run_code(self):
        '''
        function that will check if the the run_code command is correctly executed,
        namely if the exec_command is called with the right arguments and if the container
        is set to be available after termination
        '''
        command = "run_command"
        self.language.generate_run_command.return_value = command
        true_output = {"stdout" : ["output"], "stderr" : []}
        self.podman.exec_command.return_value = true_output
        result = self.container.run_code([1,2])
        self.podman.exec_command.assert_called_with(f'container_{self.index}',command,metrics = True,timeout = 60)
        self.assertEqual(result,true_output)
        self.assertTrue(self.container.available)

    def test_run_code_error(self):
        self.podman.exec_command.side_effect = Exception("run code error")
        with self.assertRaises(RunCodeException) as context:
            self.container.run_code([5,6])
        self.assertTrue(self.container.available)
        self.assertIn("run code error",str(context.exception))
        

    def test_compile_code(self):
        '''
        this method checks that the generate_compile_command from podman was called with the correct arguments
        and checks if compile_code is working properly
        also checks that it makes the container available after
        '''
        command = "compile command"
        self.container.language.generate_compile_command.return_value = command
        true_output = {"stdout" : ["output"], "stderr" : []}
        self.podman.exec_command.return_value = true_output
        result = self.container.compile_code()
        self.podman.exec_command.assert_called_with(f'container_{self.index}',command)
        self.assertEqual(result, true_output)
        self.assertTrue(self.container.available)

    def test_compile_code_error(self):
        self.podman.exec_command.side_effect = Exception("compile code error")
        with self.assertRaises(CompileCodeException) as context:
            self.container.compile_code()
        self.assertTrue(self.container.available)
        self.assertIn("compile code error", str(context.exception))

    def test_generate_run_command(self):
        '''
        function to check that the generate_run_command from language is called with
        the right arguments 
        '''
        true_function_name = self.metadata['signature']['name'] + "_injected" 
        true_run_command = "run command"
        self.container.language.generate_run_command.return_value = true_run_command
        command = self.container.generate_run_command([5,6])
        self.language.generate_run_command.assert_called_once_with(true_function_name,[5,6])
        self.assertEqual(command,true_run_command)

    def test_generate_run_command_error(self):
        #remove the signature
        self.container.metadata.pop('signature',None)
        with patch('sources.Container.logger') as mock_logger:
            command = self.container.generate_run_command([5,6])
             #check if the command is None, since the error is not raised
            self.assertIsNone(command)
            mock_logger.error.assert_called_once()


    def test_generate_compile_command(self):
        '''
        function to check that the generate_compile_command from language is called with
        the right arguments
        '''
        true_function_name = self.metadata['signature']['name'] + "_injected"
        true_compiler = self.metadata['compiler']
        true_compile_command = "compile command"
        self.container.language.generate_compile_command.return_value = true_compile_command
        command = self.container.generate_compile_command()
        self.language.generate_compile_command.assert_called_once_with(true_function_name,true_compiler)
        self.assertEqual(command,true_compile_command)

    def test_generate_compile_command_error(self):
        self.container.metadata.pop('signature',None)
        with patch('sources.Container.logger') as mock_logger:
            command = self.container.generate_compile_command()
            self.assertIsNone(command)
            mock_logger.error.assert_called_once()

    def test_terminate(self):
        '''
        function to check if the right methods from the podman class are called with the 
        right arguments
        '''
        self.container.remove_folder = MagicMock()
        self.container.terminate()
        self.podman.stop_container.assert_called_once_with(f'container_{self.index}')
        self.podman.remove_container.assert_called_once_with(f'container_{self.index}')
        self.podman.remove_image.assert_called_once_with(f'image_{self.index}', f'image_tag_{self.index}')
        self.container.remove_folder.assert_called_once()

    def test_terminate_error(self):
        self.podman.stop_container.side_effect = Exception("stop error")
        with self.assertRaises(TerminateException) as context:
            self.container.terminate()
        self.assertIn("stop error",str(context.exception))

    def test_clear(self):
        '''
        function to check if the exec_command method is correctly called with the right arguments
        and check if the container's state is available before and after the clear() command is called
        '''
        self.assertTrue(self.available)
        self.container.remove_folder = MagicMock()
        true_output = {"stdout" : ["output"], "stderr": []}
        self.podman.exec_command.return_value = true_output
        self.container.clear()
        self.container.remove_folder.assert_called_once()
        self.assertTrue(self.container.available)

    def test_clear_error(self):
        self.container.remove_folder = MagicMock(side_effect = Exception("clear error"))
        self.podman.exec_command.return_value = {"stdout" : ["test"], "stderr" : []}
        with self.assertRaises(ClearException) as context:
            self.container.clear()
        self.assertIn("clear error",str(context.exception))
        self.assertFalse(self.container.available)


    def test_remove_folder(self):
        '''function to check if the temporary folder created is removed'''
        os.makedirs(self.container.mounting_path,exist_ok=True)
        mock_file = os.path.join(self.container.mounting_path, "mock.txt")
        with open (mock_file, "w") as f :
            f.write("mock")
        self.container.remove_folder()
        self.assertFalse(os.path.exists(self.container.mounting_path))

    def test_remove_folder_error(self):
        os.makedirs(self.container.mounting_path,exist_ok=True)
        mock_file = os.path.join(self.container.mounting_path,"mock.txt")
        with open(mock_file,"w") as f:
            f.write("mock content")
        with patch('sources.Container.os.rmdir', side_effect = Exception("rmdir error")):
            with self.assertRaises(OSError) as context:
                self.container.remove_folder()
        self.assertEqual(str(context.exception), "Failed to remove folder")

    
    def test_inject(self):
        #make sure that the mounting path is clean 
        if os.path.exists(self.container.mounting_path):
            shutil.rmtree(self.container.mounting_path)
        os.makedirs(self.container.mounting_path,exist_ok=True)
        #reset the mock
        self.language.inject.reset_mock()
        self.container.run_as_is = False
        function_name = self.metadata['signature']['name']
        signature = self.metadata['signature']
        self.container.inject()
        file_extension = "py"
        file_name = os.path.join(self.container.mounting_path,f"{function_name}.{file_extension}")
        injected_file = os.path.join(self.container.mounting_path, f"{self.metadata['signature']['name']}_injected.{file_extension}")

        self.language.inject.assert_called_once_with(file_name,injected_file,signature)
        self.assertFalse(os.path.exists(file_name))

    def test_inject_run_as_is(self):
        #make sure that the mounting path is clean 
        if os.path.exists(self.container.mounting_path):
            shutil.rmtree(self.container.mounting_path)
        self.container.run_as_is = True
        self.language.get_extention.return_value = "py"
        function_name = self.metadata['signature']['name']
        self.container.inject()
        injected_file = os.path.join(self.container.mounting_path, "function_injected.py")
        #check that the file exists and it containts the code that it should
        self.assertTrue(os.path.exists(injected_file))
        with open(injected_file, "r") as f:
            code = f.read()
        self.assertEqual(code,self.metadata['code'])

    def test_change_code(self):
        self.container.clear = MagicMock()
        self.container.check_signature = MagicMock()
        self.container.inject = MagicMock()
        self.container.copy_helper_files = MagicMock()
        self.container.upload_code = MagicMock()
        self.container.compile_code = MagicMock()
        self.container.available = True
        self.container.change_code()
        self.container.clear.assert_called_once()
        self.container.check_signature.assert_called_once()
        self.container.inject.assert_called_once()
        self.container.upload_code.assert_called_once()
        self.container.compile_code.assert_called_once()
        self.assertTrue(self.container.available)

    def test_change_code_error(self):
        self.container.compile_code = MagicMock(side_effect = Exception("change code error"))
        with self.assertRaises(ChangeCodeException) as context:
            self.container.change_code()
        self.assertIn("change code error",str(context.exception))
        self.assertTrue(self.container.available)

    def test_upload_code(self):
        #create some files in the mounting path
        os.makedirs(self.container.mounting_path,exist_ok=True)
        mock_file_1 = os.path.join(self.container.mounting_path, "mock1.txt")
        mock_file_2 = os.path.join(self.container.mounting_path, "mock2.txt")
        with open(mock_file_1, "w") as f:
            f.write("code1")
        with open(mock_file_2, "w") as f:
            f.write("code2")   
        self.container.upload_code()
        self.podman.copy_to_container.assert_any_call(mock_file_1,f"container_{self.index}")
        self.podman.copy_to_container.assert_any_call(mock_file_2,f"container_{self.index}")
        #check that it called the copy to container method twice, as the number of files
        self.assertEqual(self.podman.copy_to_container.call_count,2)

    def test_set_metadata(self):
        new_metadata = {
                "cell_id":1,
                "code": "def divide_numbers(a, b):\n\treturn a / b\n",
                "signature": {
                    "name": "divide_numbers",
                    "args":{
                        "a": "int",
                        "b": "int"
                    },
                    "return": "int"
                },
                "language": "Python",
                "version": "3.10",
                "compiler":"",
                "specs": {"libraries":"numpy"}
                        }
        
        self.container.set_metadata(new_metadata)
        self.assertDictEqual(new_metadata,self.container.metadata)

    def test_is_available(self):
        self.container.set_available(True)
        available = self.container.is_available()
        self.assertTrue(available,)

    def test_set_available(self):
        self.available = False
        self.container.set_available(True)
        self.assertTrue(self.container.available)

    def test_set_run_as_is(self):
        self.run_as_is = True
        self.container.set_run_as_is(False)
        self.assertFalse(self.container.run_as_is)
    
    def test_check_signature(self):
        true_signature = {
            "name" : "sum_numbers",
            "args" : {"a" : "int", "b" : "int"},
            "return" : "int"
        }
        self.container.language.check_signature.return_value = true_signature
        self.container.check_signature()
        self.assertDictEqual(self.container.metadata['signature'],true_signature)

    def test_check_signature_error(self):
        self.language.check_signature.side_effect = ArgumentNotFoundException("check signature error")
        with self.assertRaises(ArgumentNotFoundException) as context:
            self.container.check_signature()
        self.assertEqual("argument type not found!", str(context.exception))


if __name__ == "__main__":
    unittest.main()
import time, threading
from queue import Queue
import unittest
import tempfile
from unittest.mock import MagicMock
import os,sys,shutil,time
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)
from sources.CustomException import *
from sources.LoggerConfig import logger
from sources.Container import Container, format_output
from sources.ContainerManager import MAX_CONTAINERS,index_lock,ContainerManager
import sources.ContainerManager as container_manager_module

class MockLock:
    def release(self):
        pass

    def acquire(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self,exc_type,exc_val,exc_tb):
        pass


class TestContainerManager(unittest.TestCase):
    @staticmethod
    def constructor_container(metadata,index,run_as_is = False):
        container = MagicMock()
        container.metadata = metadata
        container.index = index
        container.run_as_is = run_as_is
        container.available = True
        container.is_available.return_value = True
        container.run_code.side_effect = lambda input, timeout: {"stdout": input , "stderr":[]}
        container.terminate.return_value = None
        container.set_available.side_effect = lambda val: setattr(container,'available',val)
        return container

    @staticmethod
    def constructor_container_with_error(metadata,index,run_as_is = False):
        container = MagicMock()
        container.metadata = metadata
        container.index = index
        container.run_as_is = run_as_is
        container.available = True
        container.is_available.return_value = True
        container.run_code.side_effect = Exception("error")
        container.terminate.return_value = None
        container.set_available.side_effect = lambda val: setattr(container,'available',val)
        return container
    
    @staticmethod 
    def constructor_container_unavailable(metadata, index, run_as_is = False):
        container = MagicMock()
        container.metadata = metadata
        container.index = index
        container.run_as_is = run_as_is
        container.available = False
        container.is_available.return_value = True
        container.run_code.side_effect = Exception("error")
        container.terminate.return_value = None
        container.set_available.side_effect = lambda val: setattr(container,'available',val)
        return container       

    def setUp(self):
       #make the global index__lock be a mocked locked that was defined earlier
       self.true_lock = container_manager_module.index_lock
       container_manager_module.index_lock = MockLock()
       self.addCleanup(lambda:setattr(container_manager_module,"index_lock",self.true_lock))
       #instantiate a Container Manager
       self.manager = ContainerManager(container_class=self.constructor_container)
       self.metadata = {
                'cell_id': 0,
                'code': 'def sum_numbers(a, b):\n\treturn a + b\n',
                'signature': {
                    'name': 'sum_numbers',
                    'args': [
                        'int',
                        'int'
                    ],
                    'return': 'int'
                },
                'language': 'Python',
                'version': '3.10',
                'compiler': '',
                'specs': {

                },
                'run_as_is': False
                }

    def tearDown(self):
        pass

    def test_add_container(self):
        index = self.manager.add_container(self.metadata)
        self.assertEqual(index,0)
        self.assertEqual(self.manager.container_count,1)
        self.assertIn(index,self.manager.containers)
        container, environment, timestamp = self.manager.containers[index]
        self.assertEqual(environment,self.manager.get_environment(self.metadata))
        self.assertEqual(container.metadata,self.metadata)
        self.assertEqual(container.index,index)

    def test_add_container_error(self):
        #test if it raises an error if the maximum nr of containers is reached
        for _ in range (MAX_CONTAINERS):
            self.manager.add_container(self.metadata)
        with self.assertRaises(RuntimeError) as context:
            self.manager.add_container(self.metadata)
        self.assertEqual(str(context.exception),"Maximum number of containers reached")

    def test_execute(self):
        input = [['5', '6']]
        outputs = self.manager.execute(self.metadata,inputs=input,run_as_is = False,timeout= 100)
        true_outputs = [
        {'stdout': ['5','6'], 'stderr': []}
        ]

        b = outputs[0]['stdout']
        c = outputs[0]['stderr']
        d = [{'stdout': b, 'stderr': c}]
        self.assertEqual(d,true_outputs)

    def test_execute_max_containers_reached(self):
        for _ in range (MAX_CONTAINERS):
            self.manager.add_container(self.metadata)
        for container_tuple in self.manager.containers.values():
            container, _, _ = container_tuple
            container.set_available(False)
        inputs = [["5","6"]]
        outputs = self.manager.execute(self.metadata,inputs=inputs,run_as_is = False,timeout= 100)
        true_outputs = [{'stdout': ['5', '6'], 'stderr': [], 'input': ['5', '6']}]
        self.assertEqual(self.manager.container_count,4)
        self.assertEqual(outputs,true_outputs)

    def test_execute_error(self):
        self.manager.container_class = self.constructor_container_with_error
        inputs = [["raise","6"]]
        outputs = self.manager.execute(self.metadata,inputs,timeout=1,run_as_is=False)
        self.assertDictEqual(outputs[0],{"stderr" : ['error'], "stdout" : [''],'input' : ['raise','6']})
        self.assertEqual(1,len(outputs))

    def test_execute_parallel(self):
        options = [
            {
            "cell_id" : "1",
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
                "specs": {
               }
   
            },
            {   
                "cell_id" : "2",
                "code": "std::vector<int> sort(std::vector<int> v)\n{\n    int n = v.size();\n    for (int i = 0; i < n - 1; i++)\n    {\n        for (int j = 0; j < n - i - 1; j++)\n        {\n            if (v[j] > v[j + 1])\n            {\n                std::swap(v[j], v[j + 1]);\n            }\n        }\n    }\n    return v;\n}",
                "signature": {
                    "name": "sort",
                    "args":["vector<int>"],
                    "return": "vector<int>"
                },
                "language": "cpp",
                "version": "",
                "compiler":"",
                "specs": {
                }
            }
        ]
        inputs = [["5","6"]]
        results = self.manager.execute_parallel(options=options,inputs=inputs,timeout=100)
        expected_outut_cell1 = {'1': [{'stdout': ['5','6'], 'stderr': [], 'input': ['5', '6']}]}
        expected_outut_cell2 = {'2': [{'input': ['5', '6'], 'stderr': [], 'stdout': ['5','6']}]}
        self.assertDictEqual(results[0],expected_outut_cell1)
        self.assertDictEqual(results[1],expected_outut_cell2)

    def test_execute_parallel_error(self):
        self.manager.container_class = self.constructor_container_with_error
        options = [
            {
            "cell_id" : "1",
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
                "specs": {
               }
   
            },
            {   
                "cell_id" : "2",
                "code": "std::vector<int> sort(std::vector<int> v)\n{\n    int n = v.size();\n    for (int i = 0; i < n - 1; i++)\n    {\n        for (int j = 0; j < n - i - 1; j++)\n        {\n            if (v[j] > v[j + 1])\n            {\n                std::swap(v[j], v[j + 1]);\n            }\n        }\n    }\n    return v;\n}",
                "signature": {
                    "name": "sort",
                    "args":["vector<int>"],
                    "return": "vector<int>"
                },
                "language": "cpp",
                "version": "",
                "compiler":"",
                "specs": {
                }
            }
        ]
        inputs = [["5","6"]]
        results = self.manager.execute_parallel(options,inputs,timeout=1)
        expected = [
        {'1': [{'stdout': [''], 'stderr': ['error'], 'input': ['5', '6']}]},
        {'2': [{'input': ['5', '6'], 'stderr': ['error'], 'stdout': ['']}]}
                    ]   
        self.assertEqual(results,expected)

    def test_check_containers(self):
        #check with available container
        container = self.manager.container_class(self.metadata,0,run_as_is = False)
        environment = self.manager.get_environment(self.metadata)
        self.manager.containers = {0: (container,environment,1000)}
        self.assertEqual(0,self.manager.check_containers(environment))
        container.set_available.assert_called_with(False)
        #check with unavailable container
        container_unav = self.manager.container_class(self.metadata,1,run_as_is = False)
        container_unav.is_available.return_value = False
        environment = self.manager.get_environment(self.metadata)
        self.manager.containers = {1: (container_unav,environment,1000)}
        self.assertEqual(-1,self.manager.check_containers(environment))
        container.set_available.assert_called_with(False)


    def test_get_environment(self):
        results = self.manager.get_environment(self.metadata)
        expected = {
            "language" : "Python",
            "version" : "3.10",
            "compiler" : "",
            "specs" : {}
        }
        self.assertDictEqual(results,expected)

    def test_check_container_available(self):
        #check with available container
        container = self.manager.container_class(self.metadata,0,run_as_is = False)
        environment = self.manager.get_environment(self.metadata)
        self.manager.containers = {0: (container,environment,1000)}
        result = self.manager.check_container_available(0)
        self.assertTrue(result)
        #check with unavailable container
        container_unav = self.manager.container_class(self.metadata,0,run_as_is = False)
        container_unav.is_available.return_value = False
        environment = self.manager.get_environment(self.metadata)
        self.manager.containers = {0: (container_unav,environment,1000)}
        result = self.manager.check_container_available(0)
        self.assertFalse(result)

    def test_get_oldest_container(self):
        environment = self.manager.get_environment(self.metadata)
        container1 = self.manager.container_class(self.metadata,0,run_as_is = False)
        container2 = self.manager.container_class(self.metadata,1,run_as_is = False)
        self.manager.container_count = 2
        self.manager.containers = {
            0 : (container1,environment,1000),
            1 : (container2,environment,2000)
        }
        result = self.manager.get_oldest_container()
        self.assertEqual(result,container1)
        self.assertEqual(self.manager.container_count,1)
        self.assertNotIn(0,self.manager.containers)
        container1.set_available.assert_called_with(False)

    def test_get_oldest_container_error(self):
        environment = self.manager.get_environment(self.metadata)
        container = self.manager.container_class(self.metadata,0,run_as_is = False)
        container.is_available.return_value = False
        self.manager.container_count = 1
        self.manager.containers = { 0: (container,environment,1000)}
        with self.assertRaises(NoContainerException) as context:
            self.manager.get_oldest_container()
        self.assertEqual(str(context.exception),"No container available to be removed")
        self.assertEqual(self.manager.container_count,1)

    def test_purge(self):
        environment = self.manager.get_environment(self.metadata)
        container1 = self.manager.container_class(self.metadata,0,run_as_is = False)
        container2 = self.manager.container_class(self.metadata,1,run_as_is = False)
        container3 = self.manager.container_class(self.metadata,2,run_as_is = False)
        container4 = self.manager.container_class(self.metadata,3,run_as_is = False)
        self.manager.container_count = 4
        self.manager.containers = {
            0 : (container1,environment,1000),
            1 : (container2,environment,2000),
            2 : (container3,environment,2500),
            3 : (container4,environment,3000)
        }
        self.manager.purge()
        container1.terminate.assert_called_once()
        container2.terminate.assert_called_once()
        container3.terminate.assert_called_once()
        container4.terminate.assert_called_once()
        self.assertEqual(self.manager.container_count,0)
        self.assertEqual(self.manager.containers,{})

if __name__ == "__main__":
    unittest.main()
import subprocess
import sys
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import MagicMock,patch
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir) 

from sources.Podman import Podman
from sources.CustomException import *
from sources.LoggerConfig import logger


class MockCompletedProcess:
    def __init__(self,stdout,stderr):
        self.stdout = stdout
        self.stderr = stderr

class TestPodman(unittest.TestCase):
    def setUp(self):
        self.Podman = Podman()

    def test_process_to_lines(self):
        mock_stdout = b"line1\nline2"
        mock_process = MockCompletedProcess(mock_stdout,b"")
        lines = self.Podman.process_to_lines(mock_process,"stdout")
        self.assertEqual(lines,["line1","line2"])

    def test_completed_process_to_lines(self):
        mock_stdout = b"line1\nline2"
        mock_stderr = b"error1\nerror2"
        mock_process= MockCompletedProcess(mock_stdout,mock_stderr)
        result = self.Podman.completed_process_to_lines(mock_process)
        self.assertEqual(result["stdout"],["line1","line2"])
        self.assertEqual(result["stderr"],["error1","error2"])

    def test_check_for_errors_error(self):
        mock_stdout = b""
        mock_stderr = b"Error"
        mock_process = MockCompletedProcess(mock_stdout,mock_stderr)
        with self.assertRaises(Exception) as context:
            self.Podman.check_for_errors(mock_process,Exception)
        self.assertIn("Error",str(context.exception))

    def test_check_for_errors_noerror(self):
        mock_stdout = b"line1\nline2"
        mock_stderr = b""
        mock_process = MockCompletedProcess(mock_stdout,mock_stderr)
        self.assertEqual(self.Podman.check_for_errors(mock_process,None),None)

    def test_relative_to_vm_path(self):
        #only for Windows OS
        with patch("os.name","nt"):
            result = self.Podman.relative_to_vm_path("C:\\Test\\file.txt")
        self.assertTrue(result.startswith("/mnt"))
        self.assertIn("test/file.txt",result.lower())

    def test_parse_time_output(self):
        lines = [
                    
                    "Average resident set size (kbytes): 0",
                    "Average shared text size (kbytes): 0",
                    "Average stack size (kbytes): 0",
                    "Average total size (kbytes): 0",
                    "Average unshared data size (kbytes): 0",
                    "Command being timed: \"python sum_numbers_injected.py 1 2\"",
                    "Elapsed (wall clock) time (h:mm:ss or m:ss): 0m 0.25s",
                    "Exit status: 0",
                    "File system inputs: 8792",
                    "File system outputs: 832",
                    "Involuntary context switches: 8",
                    "Major (requiring I/O) page faults: 63",
                    "Maximum resident set size (kbytes): 11284",
                    "Minor (reclaiming a frame) page faults: 9573",
                    "Page size (bytes): 4096",
                    "Percent of CPU this job got: 86%",
                    "Signals delivered: 0",
                    "Socket messages received: 0",
                    "Socket messages sent: 0",
                    "Swaps: 0",
                    "System time (seconds): 0.01",
                    "User time (seconds): 0.21",
                    "Voluntary context switches: 69"
                ]

        true_result ={
                    "Average resident set size (kbytes)": "0",
                    "Average shared text size (kbytes)": "0",
                    "Average stack size (kbytes)": "0",
                    "Average total size (kbytes)": "0",
                    "Average unshared data size (kbytes)": "0",
                    "Command being timed": "\"python sum_numbers_injected.py 1 2\"",
                    "Elapsed (wall clock) time (h:mm:ss or m:ss)": "0m 0.25s",
                    "Exit status": "0",
                    "File system inputs": "8792",
                    "File system outputs": "832",
                    "Involuntary context switches": "8",
                    "Major (requiring I/O) page faults": "63",
                    "Maximum resident set size (kbytes)": "11284",
                    "Minor (reclaiming a frame) page faults": "9573",
                    "Page size (bytes)": "4096",
                    "Percent of CPU this job got": "86%",
                    "Signals delivered": "0",
                    "Socket messages received": "0",
                    "Socket messages sent": "0",
                    "Swaps": "0",
                    "System time (seconds)": "0.01",
                    "User time (seconds)": "0.21",
                    "Voluntary context switches": "69"
                }
        result = self.Podman.parse_time_output(lines)
        self.assertDictEqual(result,true_result)

    def test_remove_metrics(self):
        mock_stderr = [
            "\tCommand being timed: \"command\"", "Error", "\tExit status:"
        ]
        result = self.Podman.remove_metrics(mock_stderr)
        self.assertEqual(result,[])

    def test_machine_exists_true(self):
        mock_stdout = b"Machine exists"
        mock_stderr = b""
        mock_process = MockCompletedProcess(mock_stdout,mock_stderr)
        with  patch("subprocess.run",return_value = mock_process):
            machine_exist = self.Podman.machine_exists("mock")
            self.assertTrue(machine_exist)


    def test_machine_exists_false(self):
        mock_stdout = b"[]"
        mock_stderr = b""
        mock_process = MockCompletedProcess(mock_stdout,mock_stderr)
        with  patch("subprocess.run",return_value = mock_process):
            machine_exist = self.Podman.machine_exists("mock")
            self.assertFalse(machine_exist)
        
    def test_clean_path(self):
        with tempfile.TemporaryDirectory() as sessions_dir:
            session_name = "session"
            sessions_path = os.path.join(sessions_dir,session_name)
            os.makedirs(sessions_path,exist_ok=True)
            mock_file = os.path.join(sessions_path,"mock.txt")
            with open(mock_file,"w") as f:
                f.write("mockyyyy")
            self.Podman.stop_container = MagicMock()
            self.Podman.remove_container = MagicMock()
            self.Podman.remove_image = MagicMock()
            self.Podman.clean_path(sessions_dir)
            self.assertFalse(os.path.exists(sessions_path))

    def test_init_machine_not_exists(self):
        self.Podman.machine_exists = MagicMock(return_value = False)
        self.Podman.clean_path = MagicMock(return_value = None)
        self.Podman.check_for_errors = MagicMock(return_value = None)
        self.Podman.print_process_output = MagicMock(return_value = None)
        mock_init = MockCompletedProcess(b"input output",b"")
        mock_start = MockCompletedProcess(b"start output",b"")
        with patch('subprocess.run',side_effect = [mock_init,mock_start]) as mock_run:
            self.Podman.init("test_machine", session_path="mock_sessions")
            self.Podman.machine_exists.assert_called_once_with("test_machine")
            self.assertEqual(mock_run.call_count,2)
            self.Podman.clean_path.assert_called_once_with("mock_sessions")
            self.assertEqual(self.Podman.check_for_errors.call_count,2)

    def test_init_machine_exists(self):
        self.Podman.machine_exists = MagicMock(return_value = True)
        self.Podman.clean_path = MagicMock(return_value = None)
        self.Podman.check_for_errors = MagicMock(return_value = None)
        mock_start = MockCompletedProcess(b"start output",b"")
        with patch('subprocess.run',return_value = mock_start) as mock_run:
            self.Podman.init("test_machine",session_path="mock_sessions")
            self.Podman.machine_exists.assert_called_once_with("test_machine")
            self.Podman.clean_path.assert_called_once_with("mock_sessions")
            self.Podman.check_for_errors.assert_called_once_with(mock_start,StartException)

    def test_stop(self):
        self.Podman.check_for_errors = MagicMock(return_value = None)
        self.Podman.print_process_output = MagicMock(return_value = None)
        mock_stop = MockCompletedProcess(b"stop",b"")
        with patch("subprocess.run",return_value = mock_stop) as mock_run:
            self.Podman.stop("test_machine")
            mock_run.assert_called_once_with(["podman","machine","stop","test_machine"],capture_output = True,shell= True)
            self.Podman.print_process_output.assert_called_once_with(mock_stop)
            self.Podman.check_for_errors.assert_called_once_with(mock_stop,StopException)
    

    def test_build_image(self):
        mock_process = MockCompletedProcess(b"build process",b"")
        with patch("subprocess.run",return_value = mock_process) as mock_run:
            self.Podman.build_image("test_image","test_tag",mount_path="mock_path",file_path="mock_file")
            mock_run.assert_called()

    def test_remove_image(self):
        mock_process = MockCompletedProcess(b"image",b"")
        with patch('subprocess.run',return_value = mock_process) as mock_run:
            self.Podman.remove_image("test-image","test-tag")
            mock_run.assert_called()

    def test_run_image(self):
        mock_process = MockCompletedProcess(b"image",b"")
        with patch('subprocess.run',return_value = mock_process) as mock_run:
            self.Podman.run_image("test-image","test-tag","container-tag")
            mock_run.assert_called()

    def test_copy_to_container(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"dummy content")
            tmp_path = tmp.name
        try:
            with patch('subprocess.run', return_value=MockCompletedProcess(b"copy output", b"")) as mock_run:
                with self.assertLogs(logger, level="INFO") as cm:
                    self.Podman.copy_to_container(tmp_path, "container_test", dest="/dest/path")
                logs = "\n".join(cm.output)
                self.assertIn("Podman copy_to_container: Copying file", logs)
                mock_run.assert_called_once()
        finally:
            os.remove(tmp_path)


    def test_exec_command(self):
        mock_process = MockCompletedProcess(b"command",b"")
        with patch('subprocess.run',return_value = mock_process) as mock_run:
            with self.assertLogs(logger,level = "INFO") as cm:
                self.Podman.exec_command("test-container",["test-command-1","test-command-2"],metrics=False,timeout=60)
            mock_run.assert_called_once()
            logs = "\n".join(cm.output)
            self.assertIn("Podman exec_command: Executing command", logs)

    def test_stop_container(self):
        mock_process = MockCompletedProcess(b"stopcontainer",b"")
        with patch('subprocess.run',return_value = mock_process) as mock_run:
            with self.assertLogs(logger,level = "INFO") as cm:
                self.Podman.stop_container("test-container")
            mock_run.assert_called_once()
            logs = "\n".join(cm.output)
            self.assertIn("Podman stop_container: Stopping container",logs)
        

    def test_remove_container(self):
        mock_process = MockCompletedProcess(b"remove",b"")
        with patch('subprocess.run',return_value = mock_process) as mock_run:
            with self.assertLogs(logger,level = "INFO") as cm:
                self.Podman.remove_container("test-container")
            mock_run.assert_called_once
            logs = "\n".join(cm.output)
            self.assertIn("Podman remove_container: Remove container",logs)

if __name__ == '__main__':
    unittest.main()


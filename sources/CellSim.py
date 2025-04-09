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
class CellSim():
    def __init__(self):
        pass

    def simulate(self, name: str, inputs: list, outputs: list) -> dict:
        results = []
        for i in range(len(inputs)):
            input = inputs[i]
            output = outputs[i]
            results.append(self.get_execution(name, input, output))
        return {name: results}

    def get_execution(self, name: str, input: list, output: list) -> dict:
        return {
            "stdout": ["\n".join(output)],
            "stderr": [],
            "metrics": self.get_metrics(name),
            "input": input
        }

    def get_metrics(self, name: str) -> dict:
        return {
          'Command being timed': f'"simulated {name}"',
          'User time (seconds)': '0.00',
          'System time (seconds)': '0.00',
          'Percent of CPU this job got': '0%',
          'Elapsed (wall clock) time (h:mm:ss or m:ss)': '0:00.00',
          'Average shared text size (kbytes)': '0',
          'Average unshared data size (kbytes)': '0',
          'Average stack size (kbytes)': '0',
          'Average total size (kbytes)': '0',
          'Maximum resident set size (kbytes)': '0',
          'Average resident set size (kbytes)': '0',
          'Major (requiring I/O) page faults': '0',
          'Minor (reclaiming a frame) page faults': '0',
          'Voluntary context switches': '0',
          'Involuntary context switches': '0',
          'Swaps': '0',
          'File system inputs': '0',
          'File system outputs': '0',
          'Socket messages sent': '0',
          'Socket messages received': '0',
          'Signals delivered': '0',
          'Page size (bytes)': '4096',
          'Exit status': '0'
        }
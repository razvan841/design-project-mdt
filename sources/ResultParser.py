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
import os,sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

import datetime
from sources.LoggerConfig import logger

class ResultParser:
    def __init__(self):
        pass

    def unpack(self, input: list) -> str:
        if len(input) < 1:
            return ""
        return input[0]

    def join(self, input: list) -> str:
        return '\n'.join(input)

    def get_cell_id(self, cell: dict) -> str:
        # cell is a dict with a single item
        return list(cell.keys())[0]

    def get_result(self, output: dict) -> str:
        return self.join(output['stdout'])

    def get_error(self, output: dict) -> str:
        return self.join(output['stderr'])

    def get_time_format(self, time: str) -> str:
        if time.count(':') > 1:
            return '%H:%M:%S.%f'
        return '%M:%S.%f'

    def get_time(self, time: str) -> datetime.timedelta:
        '''
        Helper function to convert time from string to datetime.timedelta so we can calculate total time easier
        '''
        time = time.replace('h', ':').replace('m', ':').replace('s', '').replace(" ", '')
        time_format = self.get_time_format(time)
        duration = datetime.datetime.strptime(time, time_format).time()
        return datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second, microseconds=duration.microsecond)

    def get_total_run_time(self, outputs: list) -> str:
        '''
        function to calculate total run time for a code cell. it sums up all execution times
        '''
        total_time = datetime.timedelta()
        for output in outputs:
            if 'metrics' in output.keys():
                total_time += self.get_time(output['metrics']['Elapsed (wall clock) time (h:mm:ss or m:ss)'])
        return str(total_time)

    def get_default_metrics(self, output: dict) -> dict:
        '''
        function to obtain basic metrics (executionTime, memoryUsage)
        '''
        if 'metrics' in output.keys():
            metrics = output['metrics']
            return {
                "memoryUsage": metrics['Maximum resident set size (kbytes)'] + " KB",
                "executionTime": metrics['Elapsed (wall clock) time (h:mm:ss or m:ss)']
            }
        return {
            'memoryUsage': "- KB",
            'executionTime': '- s'
        }

    def get_plugin_metrics(self, output: dict) -> dict:
        '''
        function to obtain extra metrics, such as cpu usage from the raw_output
        '''
        if 'metrics' in output.keys():
            metrics = output['metrics']
            return {
                "CPU Usage": metrics['Percent of CPU this job got'],
                "GPU Usage": "- %"
            }
        return {
            'CPU Usage': "- %",
            'GPU Usage': "- %"
        }

    def format_output(self, output: dict) -> dict:
        value = self.get_result(output)
        error_msg = self.get_error(output)
        default_metrics = self.get_default_metrics(output)
        plugin_metrics = self.get_plugin_metrics(output)
        return {
            "defaultMetrics": default_metrics,
            "pluginMetrics": plugin_metrics,
            "value": value,
            "error_msg": error_msg
        }

    def get_average_time(self, total_time: str, count: int) -> str:
        '''
        function to calculate average time needed per execution
        '''
        total_td = datetime.timedelta(hours=int(total_time.split(":")[0]),
                     minutes=int(total_time.split(":")[1]),
                     seconds=float(total_time.split(":")[2]))
        average_td = 0
        if(count > 0):
            average_td = total_td / count
        return str(average_td)

    def get_average_cpu_usage(self, outputs: list) -> str:
        '''
        function to calculate average cpu usage
        '''
        total_cpu = 0
        average_cpu = 0
        count = 0
        for output in outputs:
            if 'metrics' in output.keys():
                metrics = output['metrics']
                total_cpu += int(metrics['Percent of CPU this job got'].strip('%'))
                count += 1
        if(count > 0):
            average_cpu = total_cpu / count
        return str(round(average_cpu, 2)) + " %"

    def get_average_memory(self, outputs: list) -> str:
        '''
        function to calculate average memory usage
        '''
        total_memory = 0
        average_memory = 0
        count = 0
        for output in outputs:
            if 'metrics' in output.keys():
                metrics = output['metrics']
                total_memory += int(metrics['Maximum resident set size (kbytes)'])
                count += 1
        if(count > 0):
            average_memory = total_memory / count
        return str(round(average_memory, 2)) + " KB"

    def get_test_cases(self, input: dict) -> dict:
        '''
        helper function for get_differential
        '''
        test_cases = dict()
        for cell_dict in input:
            for cell_id, test_results in cell_dict.items():
                for idx in range(len(test_results)):
                    test = test_results[idx]
                    test_input = test["input"]
                    output_value = self.get_result(test)
                    error_msg = self.get_error(test)

                    if idx not in test_cases:
                        test_cases[idx] = {
                            "test_id": str(idx),
                            "input": test_input,
                            "cells": {}
                        }

                    test_cases[idx]['cells'][cell_id] = {
                        "value": output_value,
                        "error_msg": error_msg
                    }
        return test_cases

    def get_differential(self, input: dict) -> dict:
        '''
        Checks if all code cells return the same output for each input
        If not, creates a dict, highlighting the different outputs between code cells
        '''
        test_cases = self.get_test_cases(input)
        test_count = len(test_cases.keys())
        matched = 0
        failed_tests = []

        for test_id, test in test_cases.items():
            cells = test['cells']
            cells_outputs = set(cell["value"] for cell in cells.values())

            if len(cells_outputs) == 1:
                matched += 1
            else:
                failed_tests.append(test)
        return {
            "test_count": str(test_count),
            "matched": str(matched),
            "no_match": str(test_count - matched),
            "failed": failed_tests
        }

    def parse(self, input: list) -> dict:
        '''
        Main result parsing function
        Retrieves information from the raw_output and it formats it nicely for the frontend
        '''
        parsed = {}
        for cell in input:
            cell_id = self.get_cell_id(cell)
            raw_outputs = cell[cell_id]
            total_run_time = self.get_total_run_time(raw_outputs)
            average_memory_usage = self.get_average_memory(raw_outputs)
            average_cpu_usage = self.get_average_cpu_usage(raw_outputs)
            average_time = self.get_average_time(total_run_time, len(raw_outputs))
            outputs = {}
            for index in range(len(raw_outputs)):
                output = raw_outputs[index]
                outputs[str(index)] = self.format_output(output)
            parsed[cell_id] = {
                "outputs": outputs,
                "average_memory_usage": average_memory_usage,
                "average_cpu_usage": average_cpu_usage,
                "average_time": average_time,
                "total_run_time": total_run_time
            }
        parsed["differential"] = self.get_differential(input)
        return parsed
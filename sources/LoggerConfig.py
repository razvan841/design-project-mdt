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
import logging
import colorlog

'''
Logger Configuration file
Logger levels:
NOTSET=0
DEBUG=10
INFO=20
WARN=30
ERROR=40
CRITICAL=50
'''

STDERR_LEVEL = 15

logger = logging.getLogger("flask_app")
exec_logger = logging.getLogger("exec_logger")
# Change this value based on the desired logging level
logger.setLevel(STDERR_LEVEL)
exec_logger.setLevel(logging.INFO)

logging.addLevelName(STDERR_LEVEL, "STDERR")

def stderr_log(self, message, *args, **kwargs):
    if self.isEnabledFor(STDERR_LEVEL):
        self._log(STDERR_LEVEL, message, args, **kwargs)

logging.Logger.stderr = stderr_log

# Coloring scheme for levels
console_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "STDERR": "purple",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# Add handlers for terminal and file logging
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
exec_file_formatter = logging.Formatter("%(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

file_handler = logging.FileHandler("backend.log")
file_handler.setFormatter(file_formatter)

exec_file_handler = logging.FileHandler("exec.log")
exec_file_handler.setFormatter(exec_file_formatter)

if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

if not exec_logger.hasHandlers():
    exec_logger.addHandler(exec_file_handler)


def clear_exec_log_file():
    '''
    Function for clearing the exec.log file.
    After finishing a request, important to clear this file so the status resets to 0 for the next request
    '''
    with open("exec.log", "w"):
        pass
    for handler in exec_logger.handlers:
        handler.close()
        exec_logger.removeHandler(handler)

    exec_file_handler = logging.FileHandler("exec.log")
    exec_file_handler.setFormatter(exec_file_formatter)
    exec_logger.addHandler(exec_file_handler)
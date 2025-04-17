import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(parent_dir)
from sources.languages.TSLanguage import TSLanguage
from sources.CustomException import *

ts = TSLanguage()

signature = {
    "name": "sum",
    "return": "int",
    "args": {
        "a": "int",
        "b": "int"
    }
}


ts.inject("test_code.ts", "test_code_injected.ts", signature)

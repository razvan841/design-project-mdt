import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(parent_dir)
from sources.languages.GoLanguage import GoLanguage
from sources.CustomException import *

go = GoLanguage()

signature = {
    "name": "sum",
    "return": "bool",
    "args": {
        "a": "bool",
        "b": "bool"
    }
}


go.inject("test_code.go", "test_code_injected.go", signature)

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(parent_dir)
from sources.languages.RustLanguage import RustLanguage
from sources.CustomException import *

rs = RustLanguage()

signature = {
    "name": "sum",
    "return": "Vec<i32>",
    "args": {
        "a": "Vec<String>",
        "b": "Vec<bool>"
    }
}


rs.inject("test_code.rs", "test_code_injected.rs", signature)

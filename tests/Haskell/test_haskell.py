import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(parent_dir)
from sources.languages.HaskellLanguage import HaskellLanguage

hs = HaskellLanguage()

signature = {
    "name": "sumTwo",
    "return": "Int",
    "args": {
        "a": "Int",
        "b": "Int"
    }
}


hs.inject("test_code.hs", "test_code_injected.hs", signature)

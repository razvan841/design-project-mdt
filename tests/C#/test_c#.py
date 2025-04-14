import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.append(parent_dir)
from sources.languages.CSLanguage import CSLanguage
from sources.CustomException import *

cs = CSLanguage()

signature = {
    "name": "SumNestedFloatList",
    "return": "float",
    "args": {
        "b": "List<List<float>>"
    }
}


cs.inject("test_code.cs", "test_code_injected.cs", signature)
# cs.docker_maker.generate_dockerfile("8.0", "dotnet", "test", [], 0)
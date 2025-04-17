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

from sources.languages.Language import Language
from sources.languages.PyLanguage import PyLanguage
from sources.languages.CppLanguage import CppLanguage
from sources.languages.JSLanguage import JSLanguage
from sources.languages.PHPLanguage import PHPLanguage
from sources.languages.JavaLanguage import JavaLanguage
from sources.languages.GoLanguage import GoLanguage
from sources.languages.CSLanguage import CSLanguage
from sources.languages.RustLanguage import RustLanguage
from sources.languages.TSLanguage import TSLanguage
from sources.CustomException import LanguageNotFoundException
from sources.LoggerConfig import logger


SUPPORTED_LANGUAGES = ["python", "cpp", "javascript", "php", "java", "go", "c#", "rust", "typescript"]
class LanguageFactory:
    def __init__(self):
        pass

    def get_language(self, language: str) -> Language:
        '''
        Function that returns the language object based on the string
        '''
        match language.lower():
            case "python":
                return PyLanguage()
            case "cpp":
                return CppLanguage()
            case "js" | "javascript":
                return JSLanguage()
            case "php":
                return PHPLanguage()
            case "java":
                return JavaLanguage()
            case "go":
                return GoLanguage()
            case "c#" | "cs":
                return CSLanguage()
            case "rust":
                return RustLanguage()
            case "typescript" | "ts":
                return TSLanguage()
            case _:
                logger.error(f"Language Factory get_language: Language not found: {language}")
                raise LanguageNotFoundException(f"Language not found: {language}")
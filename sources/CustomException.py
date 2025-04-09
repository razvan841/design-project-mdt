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
class InjectException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class InitException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class StartException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class StopException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ImageBuildException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ImageRemoveException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ImageRunException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class CopyException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ExecutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ContainerStopException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ContainerRemoveException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class LanguageNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class InitContainerException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class RunCodeException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class CompileCodeException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class TerminateException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ClearException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ChangeCodeException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class MaxAttemptException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class NoContainerException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class RunCodeTimeoutException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class ArgumentNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class TypeNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class GenerateTestCasesException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class LanguageNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class ContainerFileCommunicationException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
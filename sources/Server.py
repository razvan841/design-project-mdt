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
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os, sys, json, shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

from sources.ContainerManager import ContainerManager
from sources.Podman import Podman, podman
from sources.ResultParser import ResultParser
from sources.LoggerConfig import logger, exec_logger, clear_exec_log_file
from sources.LanguageFactory import LanguageFactory, SUPPORTED_LANGUAGES
from sources.TestCasesGenerator import TestCasesGenerator, DEFAULT_PARAMETERS
from sources.CellSim import CellSim

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_FOLDER = os.path.join(BASE_DIR, "..", "projects")

class FlaskServer:
    def __init__(self, container_manager: ContainerManager = ContainerManager, podman_instance: Podman = podman, language_factory: LanguageFactory = LanguageFactory):
        self.app = Flask(__name__)
        CORS(self.app)
        self.ready = False
        self.make_sessions()
        self.manager = container_manager()
        self.podman = podman_instance
        self.language_factory = language_factory()
        self.podman.init()
        self.setup_routes()
        clear_exec_log_file()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({"message": "Welcome to the Code Execution API!"})

        @self.app.route('/api/v1/execute_code', methods=['GET', 'POST'])
        def execute_code():
            if not self.ready:
                return jsonify({"message": {"status": 503, "error_message": "Server is not ready yet. Please wait!"}}), 503
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"message": {"status": 400, "error_message": "Invalid JSON input."}}), 400

                options = data.get("message", {}).get("options", [])
                input_data = data.get("message", {}).get("input", [])
                output_data = data.get("message", {}).get("output", [])
                generate_test_cases = data.get("message", {}).get("generate_test_cases", False)
                test_count = data.get("message", {}).get("test_cases_count", 25)
                test_signature = data.get("message", {}).get("test_cases_signature", [])
                test_parameters = data.get("message", {}).get("test_cases_parameters", DEFAULT_PARAMETERS)
                timeout = data.get("message", {}).get("timeout", 60)
                configurations = data.get("message", {}).get("configurations", {})
                float_epsilon = configurations.get("float_epsilon", 0.0001)
                exec_logger.info(f"Code cells: {len(options)}")

                if not (input_data or (generate_test_cases and test_count > 0)):
                    logger.error("Server execute_code: Test cases are missing! Add manual tests or generate tests automatically")
                    return jsonify({"message" : {"status": 400, "error_message": "Test cases are missing! Add manual tests or generate tests automatically"}}), 400

                if not generate_test_cases:
                    if len(input_data) != len(output_data):
                        logger.error("Server execute_code: Manual testing must provide equal number of inputs and outputs")
                        return jsonify({"message" : {"status": 400, "error_message": "Input and output lists must have equal length"}}), 400

                if generate_test_cases == True:
                    try:
                        generator = TestCasesGenerator()
                        generated_inputs = generator.generate_test_cases(test_signature, test_count, test_parameters)
                        input_data = generated_inputs

                    except Exception as e:
                        logger.error("Server execute_code: Test generation failed")
                        return jsonify({"message": {"status": 400, "error_message": "Failed to generate test cases: check types to be correct"}}), 400

                if timeout < 5:
                    logger.error("Server execute_code: error: Timeout value needs to be at least 5 seconds")
                    return jsonify({"message": {"status": 400, "error_message": "Timeout value needs to be at least 5 seconds"}}), 400

                if not options:
                    logger.error("Server execute_code: error: Options list cannot be empty.")
                    return jsonify({"message": {"status": 400, "error_message": "Options list cannot be empty."}}), 400

                return_type = options[0]['signature']['return']
                raw_outputs = self.manager.execute_parallel(options, input_data, timeout)

                # if manual testing, simulate provided outputs as cell output:
                if not generate_test_cases:
                    output_cell = CellSim().simulate(name="expected_output", inputs=input_data, outputs=output_data)
                    raw_outputs.append(output_cell)

                result_parser = ResultParser()
                outputs = result_parser.parse(raw_outputs, return_type, float_epsilon)
                clear_exec_log_file()

            except Exception as e:
                logger.error(f"Server execute_code: {str(e)}")
                clear_exec_log_file()
                return jsonify({"message": {"status": 400, "error_message": f"{str(e)}"}}), 400

            logger.info("Successfully handled execute code request")
            response_json = json.dumps(obj=outputs, indent=2, sort_keys=False)
            return Response(response_json, mimetype="application/json"), 200

        @self.app.route('/api/v1/get_projects', methods=['GET'])
        def get_projects():
            '''
            API for retrieving all user project names. Helpful for porting to a remote server
            '''
            try:
                if not os.path.exists(PROJECTS_FOLDER):
                    logger.error("error get_projects: Projects folder not found.")
                    return jsonify({"error": "Projects folder not found."}), 404

                projects = [p for p in os.listdir(PROJECTS_FOLDER) if os.path.isfile(os.path.join(PROJECTS_FOLDER, p))]
                logger.info("Server get_projects: Successfully handled get projects request")
                return jsonify({"projects": projects}), 200
            except Exception as e:
                logger.error(f"Server get_projects: error: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/v1/get_project', methods=['GET'])
        def get_project():
            '''
            API for retrieving a project. Helpful for porting to a remote server
            '''
            project_name = request.args.get('name')
            if not project_name:
                return jsonify({"error": "Missing 'name' query parameter"}), 400

            project_name = project_name.strip() + ".json"
            project_path = os.path.join(PROJECTS_FOLDER, project_name)

            if not os.path.exists(project_path):
                logger.error("Server get_project: error: Project not found")
                return jsonify({"error": "Project not found"}), 404

            try:
                with open(project_path, 'r', encoding='utf-8') as file:
                    project_data = json.load(file)
                logger.info("Server get_project: Successfully handled get project request")
                return jsonify(project_data), 200
            except json.JSONDecodeError:
                logger.error("Server get_project: error: Invalid JSON format in project file")
                return jsonify({"error": "Invalid JSON format in project file"}), 500

        @self.app.route('/api/v1/save_project', methods=['POST'])
        def save_project():
            '''
            API for saving a project. Helpful for porting to a remote server
            '''
            project_name = request.args.get('name')
            if not project_name:
                logger.error("Server save_project: error: Missing 'name' query parameter")
                return jsonify({"error": "Missing 'name' query parameter"}), 400
            project_name = project_name.strip() + '.json'

            if not os.path.exists(PROJECTS_FOLDER):
                os.makedirs(PROJECTS_FOLDER)

            project_path = os.path.join(PROJECTS_FOLDER, project_name)
            try:
                project_data = request.get_json()
                if not project_data:
                    logger.error("Server save_project: error: Missing or invalid JSON body")
                    return jsonify({"error": "Missing or invalid JSON body"}), 400

                with open(project_path, 'w', encoding='utf-8') as file:
                    json.dump(project_data, file, indent=4)
                logger.info("Server save_project: Successfully handled save project request")
                return jsonify({"message": f"Project '{project_name}' saved successfully"}), 201
            except Exception as e:
                logger.error(f"Server save_project: error: {str(e)}")
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/v1/purge_containers', methods=['DELETE'])
        def purge_containers():
            '''
            API for cleaning the backend. It removes all podman containers, images and folders from the sessions folder
            '''
            self.manager.purge()
            logger.info("Server purge_containers: Successfully handled purge containers request")
            return jsonify({"message": "Successfully purged containers"}), 200

        @self.app.route('/api/v1/versions_compilers', methods=['GET'])
        def get_versions_compilers():
            '''
            API for obtaining all supported language, with their versions and compilers
            '''
            language_name = request.args.get('language')
            if not language_name:
                logger.error("Server get_versions_compilers: error: Missing 'name' query parameter")
                return jsonify({"error": "Missing 'name' query parameter"}), 400

            response = {}

            if language_name == "all":
                for language in SUPPORTED_LANGUAGES:
                    lang = self.language_factory.get_language(language)
                    versions = lang.get_available_versions()
                    compilers = lang.get_available_compilers()
                    dict_versions_compilers = {
                        "versions": versions,
                        "compilers": compilers
                    }
                    response[language] = dict_versions_compilers
                return response

            language = self.language_factory.get_language(language=language_name)
            versions = language.get_available_versions()
            compilers = language.get_available_compilers()
            response['versions'] = versions
            response['compilers'] = compilers
            return jsonify(response), 200

        @self.app.route('/api/v1/status_execution', methods=['GET'])
        def status_execution():
            '''
            API for obtaining the status of the execution. It returns a float between 0 and 1.
            '''
            try:
                status = 0
                status = round(self.manager.calculate_status(), 3)
                response = {
                    'status': status
                }
                return jsonify(response), 200
            except Exception:
                response = {
                    'status': 0
                }
                return jsonify(response), 200

    def run(self, host: str ='localhost', port: int =5000, debug: bool=True) -> None:
        logger.info("Server run: Starting the server...")
        self.remove_cache()
        self.ready = True
        self.app.run(host=host, port=port, debug=debug)

    def remove_cache(self) -> None:
        shutil.rmtree(os.path.join(current_dir, "__pycache__"), ignore_errors=True)
        shutil.rmtree(os.path.join(current_dir, "languages", "__pycache__"), ignore_errors=True)

    def make_sessions(self) -> None:
        folders = os.listdir(parent_dir)
        if "sessions" not in folders:
            logger.info("Server setup: sessions folder not found, creating...")
            os.mkdir(os.path.join(parent_dir, "sessions"))


if __name__ == '__main__':
    logger.info("Server: Initializing server...")
    server = FlaskServer()
    server.run(debug= False)
import flask
from pathlib import Path
from os import getenv
from http import HTTPStatus
from typing import *

from static.dependencies.version import APIVersion
from static.dependencies.functions import APITools
from static.dependencies.endpoints import Endpoints


app = flask.Flask(__name__)
app.app_context().push()

latest_api_version = APIVersion.Latest().version

google_gemini_api_keys = list()
start_number = 0
while True:
    start_number += 1
    value = getenv(f'GOOGLE_GEMINI_API_KEY_{start_number}')
    if value: google_gemini_api_keys.append(str(value))
    else: break


def show_error_page(error_code: int, custom_error_name: str = None):
    if not custom_error_name:
        error_name = HTTPStatus(error_code).phrase
        custom_error_name = error_name

    return flask.render_template('web_errors.html', error_code=error_code, error_name=custom_error_name), error_code

@app.errorhandler(404)
def error_404(e: Exception) -> Tuple[str, int]: return show_error_page(404)

@app.errorhandler(429)
def error_429(e: Exception) -> Tuple[str, int]: return show_error_page(429)

@app.errorhandler(500)
def error_500(e: Exception) -> Tuple[str, int]: return show_error_page(500)

@app.errorhandler(503)
def error_503(e: Exception) -> Tuple[str, int]: return show_error_page(503)

@app.route('/', methods=['GET'])
def initial_page() -> Union[str, Any]:
    APITools.check_main_request(flask.request.remote_addr, None)
    return flask.render_template('index.html')

@app.route('/docs/', methods=['GET'])
def documentation_page() -> Union[str, Any]:
    APITools.check_main_request(flask.request.remote_addr, None)
    return flask.render_template('documentation.html')

@app.route('/api/', methods=['GET'])
def api() -> Union[Dict[str, Union[bool, str]], Any]:
    APITools.check_main_request(flask.request.remote_addr, None)
    return flask.redirect(f'/api/{latest_api_version}/status', code=302)

@app.route('/api/<version>/', methods=['GET'])
def api_version(version: str) -> Union[Dict[str, Union[bool, str]], Any]:
    APITools.check_main_request(flask.request.remote_addr, None)
    return flask.redirect(f'/api/{version}/status', code=302)

@app.route('/api/<version>/status/', methods=['GET'])
def api_version_status(version: str) -> Union[Dict[str, Union[bool, str]], Any]:
    APITools.check_main_request(flask.request.remote_addr, None)
    return Endpoints.api_version(version).get_status(version)

@app.route(f'/api/<version>/randomizer/int-number/', methods=['GET'])
def randomizer_int_number(version: str) -> Any:
    APITools.check_main_request(flask.request.remote_addr, (0, 120, 6000, 16000), version, latest_api_version)
    return Endpoints.api_version(version).Randomizer.int_number(flask.request.args.get('min'), flask.request.args.get('max'))

@app.route('/api/<version>/randomizer/float-number/', methods=['GET'])
def randomizer_float_number(version: str) -> Any:
    APITools.check_main_request(flask.request.remote_addr, (0, 120, 6000, 16000), version, latest_api_version)
    return Endpoints.api_version(version).Randomizer.float_number(flask.request.args.get('min'), flask.request.args.get('max'))

@app.route('/api/<version>/requester/user-agent/', methods=['GET'])
def requester_user_agent(version: str) -> Any:
    APITools.check_main_request(flask.request.remote_addr, (1, 60, 4000, 12000), version, latest_api_version)
    return Endpoints.api_version(version).Requester.user_agent(flask.request.user_agent.string, flask.request.args.get('value'))

@app.route('/api/<version>/requester/ip-address/', methods=['GET'])
def requester_ip_address(version: str) -> Any:
    APITools.check_main_request(flask.request.remote_addr, (1, 60, 3000, 10000), version, latest_api_version)
    return Endpoints.api_version(version).Requester.ip_address(flask.request.remote_addr, flask.request.args.get('value'))

@app.route('/api/<version>/scraper/media-youtube.com/', methods=['GET'])
def scraper_youtube_com(version: str) -> Any:
    APITools.check_main_request(flask.request.remote_addr, (1, 30, 2000, 6000), version, latest_api_version)
    return Endpoints.api_version(version).Scraper.youtube_com(flask.request.args.get('url'))


if __name__ == '__main__':
    app.config['CACHE_TYPE'] = 'simple'
    app.config['JSON_SORT_KEYS'] = True
    app.template_folder = Path(Path.cwd(), 'templates').resolve()
    app.run(load_dotenv=True, host='0.0.0.0', port=13579, threaded=True, debug=False)

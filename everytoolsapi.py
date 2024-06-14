import flask
from flask_limiter import util as flask_limiter_utils, Limiter
from flask_caching import Cache
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from logging.config import dictConfig
from dotenv import load_dotenv
from os import getenv
from yaml import safe_load as yaml_safe_load
from pathlib import Path
from typing import *

from static.data.version import APIVersion
from static.data.functions import APITools, LimiterTools, CacheTools
from static.data.endpoints import APIEndpoints


# Load the environment variables
load_dotenv()

# Configuration class
class Config:
    def __init__(self, **entries: Dict[str, Any]) -> None:
        for key, value in entries.items():
            if isinstance(value, dict):
                value = Config(**value)

            self.__dict__[key] = value


# Setup Flask application
app = flask.Flask(__name__)

# Setup Flask logging configuration
logging_config = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
}
dictConfig(logging_config)

# Setup Flask limiter with Redis
limiter = Limiter(flask_limiter_utils.get_remote_address, app=app, storage_uri=str(getenv('REDIS_URL')))

# Setup Flask cache with Redis
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = str(getenv('REDIS_HOST'))
app.config['CACHE_REDIS_PORT'] = int(getenv('REDIS_PORT'))
app.config['CACHE_REDIS_DB'] = int(getenv('REDIS_DB'))
app.config['CACHE_REDIS_PASSWORD'] = str(getenv('REDIS_PASSWORD'))
app.config['CACHE_REDIS_URL'] = str(getenv('REDIS_URL'))
cache = Cache(app)

# Setup Talisman for security headers (with custom options), CSRF protection and Compress for response compression
talisman = Talisman(app, content_security_policy={'default-src': ["'self'", 'https://cdnjs.cloudflare.com'], 'style-src': ["'self'", "'unsafe-inline'", 'https://cdnjs.cloudflare.com'], 'script-src': ["'self'", 'https://cdnjs.cloudflare.com']})
csrf = CSRFProtect(app)
compression = Compress(app)


# Setup main routes
@app.route('/', methods=['GET'])
@limiter.limit(LimiterTools.gen_ratelimit_message(per_min=60))
@cache.cached(timeout=300, make_cache_key=CacheTools.gen_cache_key)
def initial_page() -> flask.render_template:
    # Example usage: GET /
    return flask.render_template('index.html')


# Setup API routes
_parser__user_agent = APIEndpoints.v2.parser.user_agent
@app.route(f'/api/<query_version>{_parser__user_agent.endpoint_url}', methods=_parser__user_agent.allowed_methods)
@limiter.limit(_parser__user_agent.ratelimit)
@cache.cached(timeout=_parser__user_agent.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__user_agent(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/user-agent?query=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__user_agent.run(APITools.extract_request_data(flask.request)))


_parser__url = APIEndpoints.v2.parser.url
@app.route(f'/api/<query_version>{_parser__url.endpoint_url}', methods=_parser__url.allowed_methods)
@limiter.limit(_parser__url.ratelimit)
@cache.cached(timeout=_parser__url.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__url(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/url?query=https://example.com/path?project=EveryTools API&version=v2#documentation
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__url.run(APITools.extract_request_data(flask.request)))


_parser__time_hms = APIEndpoints.v2.parser.sec_to_hms
@app.route(f'/api/<query_version>{_parser__time_hms.endpoint_url}', methods=_parser__time_hms.allowed_methods)
@limiter.limit(_parser__time_hms.ratelimit)
@cache.cached(timeout=_parser__time_hms.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__time_hms(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/sec-to-hms?query=13500
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__time_hms.run(APITools.extract_request_data(flask.request)))


_parser__email = APIEndpoints.v2.parser.email
@app.route(f'/api/<query_version>{_parser__email.endpoint_url}', methods=_parser__email.allowed_methods)
@limiter.limit(_parser__email.ratelimit)
@cache.cached(timeout=_parser__email.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__email(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/email?query=everytoolsapi@example.com
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__email.run(APITools.extract_request_data(flask.request)))


_parser__text_counter = APIEndpoints.v2.parser.text_counter
@app.route(f'/api/<query_version>{_parser__text_counter.endpoint_url}', methods=_parser__text_counter.allowed_methods)
@limiter.limit(_parser__text_counter.ratelimit)
@cache.cached(timeout=_parser__text_counter.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__text_counter(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/text-counter?query=Hi! I'm EveryTools API. #v2
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__text_counter.run(APITools.extract_request_data(flask.request)))


_parser__text_lang_detector = APIEndpoints.v2.parser.text_lang_detector
@app.route(f'/api/<query_version>{_parser__text_lang_detector.endpoint_url}', methods=_parser__text_lang_detector.allowed_methods)
@limiter.limit(_parser__text_lang_detector.ratelimit)
@cache.cached(timeout=_parser__text_lang_detector.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__text_lang_detector(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/text-lang-detector?query=Olá, bom dia! Como você está?
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__text_lang_detector.run(APITools.extract_request_data(flask.request)))


_parser__text_translator = APIEndpoints.v2.parser.text_translator
@app.route(f'/api/<query_version>{_parser__text_translator.endpoint_url}', methods=_parser__text_translator.allowed_methods)
@limiter.limit(_parser__text_translator.ratelimit)
@cache.cached(timeout=_parser__text_translator.timeout, make_cache_key=CacheTools.gen_cache_key)
def parser__text_translator(query_version: str) -> flask.jsonify:
    # Example usage: GET /api/v2/parser/text-translator?query=Welcome to my API!&src_lang=en&dest_lang=pt-br
    if not APIVersion.is_latest_api_version(query_version): return APIVersion.send_invalid_api_version_response(query_version)
    return flask.jsonify(_parser__text_translator.run(APITools.extract_request_data(flask.request)))


if __name__ == '__main__':
    # Load the configuration file
    current_path = Path(__file__).parent
    config_path = Path(current_path, 'config.yml')
    config = Config(**yaml_safe_load(config_path.open('r')))

    # Setting up Flask default configuration
    app.static_folder = Path(current_path, config.flask.staticFolder)
    app.template_folder = Path(current_path, config.flask.templateFolder)

    # Run the web server with the specified configuration
    app.run(host=config.flask.host, port=config.flask.port, threaded=config.flask.threadedServer, debug=config.flask.debugMode)

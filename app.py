import os
from flask import Flask, request
from dotenv import load_dotenv
import logging
import json

load_dotenv()
app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

if os.getenv("ALLOWED_KEYS") == "" or os.getenv("ALLOWED_KEYS") is None:
    if os.getenv("ALLOWED_KEYS").split(",")[0] == "":
        raise ValueError(f"No keys found in ALLOWED_KEYS environment variable. \nHere is a random key: {os.urandom(128)}")
logger.info(f"Loaded {len(os.getenv('ALLOWED_KEYS').split(','))} keys from ALLOWED_KEYS environment variable")
if os.getenv("BYPASS_KEY_CHECKING").lower() == "true":
    logger.warning("BYPASS_KEY_CHECKING is set to True. This means that the API key checking is disabled. This is not recommended for production environments.")


def process_return(status: str, data: str | dict, http_code: int | None = None) -> tuple:
    status_types = ["error", "success"]
    if status not in status_types:
        raise ValueError(f"Invalid status. status must be any of {status_types} not {status}")
    if type(status) is not str:
        raise TypeError(f"status must be a string not {type(status)}")
    if type(data) is dict:
        data = json.dumps(data)
    elif type(data) is not str:
        raise TypeError(f"data must be a string or dict not {type(data)}")
    if status in status_types and http_code is None:
        if status == "error":
            code = 500 # Internal Server Error
        else:
            code = 200 # OK
        return json.dumps({"status": status, "data": data}), code, {"Content-Type": "application/json"}
    elif http_code is not None:
        if type(http_code) is not int:
            raise TypeError(f"http_code must be an int not {type(http_code)}")
        if status in status_types:
            return json.dumps({"status": status, "data": data}), http_code, {"Content-Type": "application/json"}
        else:
            raise ValueError(f"Invalid status. http_code must be set or status must be 'error' or 'success' not {status}")
    else:
        raise ValueError(f"Invalid status. http_code must be set or status must be 'error' or 'success' not {status}")


def check_key(key):
    return key in os.getenv("ALLOWED_KEYS").split(",") or os.getenv("BYPASS_KEY_CHECKING").lower() == "true"


@app.route('/', methods=['GET'])
def index():
    if check_key(request.headers.get("SS-API-KEY")):
        # gather a list of endpoints
        endpoints = app.url_map.iter_rules()
        return process_return("success", {"endpoints": [str(rule) for rule in endpoints]})
    else:
        return process_return("error", "Invalid API key")

@app.route('/database', methods=['GET', 'POST', 'DELETE'])
def database():
    if check_key(request.headers.get("SS-API-KEY")):
        if request.method == 'GET':
            return process_return("success", "GET database")
        elif request.method == 'POST':
            return process_return("success", "POST database")
        elif request.method == 'DELETE':
            return process_return("success", "DELETE database")
    else:
        return process_return("error", "Invalid API key")

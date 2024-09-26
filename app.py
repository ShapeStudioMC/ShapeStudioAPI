import os
from flask import Flask, request
from dotenv import load_dotenv
import logging
import json

load_dotenv()
app = Flask(__name__)

logger = logging.getLogger(__name__)


def process_return(status: str, data: str | dict) -> tuple:
    if type(status) is not str:
        raise TypeError(f"status must be a string not {type(status)}")
    if type(data) is dict:
        data = json.dumps(data)
    elif type(data) is not str:
        raise TypeError(f"data must be a string or dict not {type(data)}")
    if status in ["error", "success"]:
        return json.dumps({"status": status, "data": data}), 200, {"Content-Type": "application/json"}
    else:
        raise ValueError(f"Invalid status. Status must be 'error' or 'success' not {status}")


def check_key(key):
    # Attempt to load the ALLOWED_KEYS environment variable
    keys = os.getenv("ALLOWED_KEYS")
    if keys is None or keys == "":
        logger.error("No keys found in ALLOWED_KEYS environment variable")
        return False
    return key in os.getenv("ALLOWED_KEYS").split(",")


@app.route('/', methods=['GET'])
def index():
    if check_key(request.headers.get("X-API-KEY")):
        return process_return("success", "Hello, World!")
    else:
        return process_return("error", "Invalid API Key")


if __name__ == '__main__':
    # DO NOT USE PYTHON CONSOLE IN PRODUCTION - USE A WSGI SERVER
    app.run()

from dotenv import load_dotenv
import os
import logging
import sys
from flask import json, Flask, jsonify, render_template
from werkzeug.exceptions import HTTPException, InternalServerError
from flask_cors import CORS
from core.util import rate_limited
from threading import Thread
from py_localtunnel.lt import run_localtunnel
from time import sleep

from api.api_v1 import api_v1_bp
import urllib

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)


load_dotenv()

VERSION = 'v1.0.0'
LAST_UPDATED = '05-04-2024-03.00 PM'


logger.warning("VERSION")
logger.warning(VERSION)
logger.warning("LAST_UPDATED")
logger.warning(LAST_UPDATED)

app = Flask(__name__,)

app.config.from_object(os.environ['APP_SETTINGS'])
CORS(app, origins=["http://localhost:3000","https://ults-genai-2024.loca.lt"], supports_credentials=True)

app.register_blueprint(api_v1_bp)

def threaded_function():
    sleep(5)
    print("running")
    try:
      run_localtunnel(5000, "ults-genai-2024", "127.0.0.1")
    except Exception as e:
      print(e)
    print("exiting")
    sleep(1)


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    logger.error(e)
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for ALL errors."""
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e
    logger.error(e)
    return handle_http_exception(InternalServerError())

@app.route("/")
@rate_limited()
def face_recognition():
    """ face_recognition page """
    return render_template('index.html')

@app.route("/register")
@rate_limited()
def face_register():
    """ face-register page """
    return render_template('register.html')
@app.route("/update")
@rate_limited()
def home_page():
    """ root page """
    return jsonify({"lastUpdated": LAST_UPDATED})


@app.route("/version")
@rate_limited()
def version():
    """ version endpoint """
    return jsonify({"version": VERSION})


@app.route("/health")
@rate_limited()
def api_health():
    """ health endpoint """
    return jsonify({"health": "up"})

if __name__ == '__main__':
    print("Password/Enpoint IP for localtunnel is:",urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n"))
    thread = Thread(target = threaded_function)
    thread.start()
    app.run(host='0.0.0.0', port=5000)
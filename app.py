from flask import Flask
import logging
from flask.logging import default_handler

formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s')
default_handler.setFormatter(formatter)

app = Flask(__name__)

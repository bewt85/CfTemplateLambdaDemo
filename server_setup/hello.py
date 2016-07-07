from flask import Flask
app = Flask(__name__)

import os
import random

@app.route('/')
def hello_world():
    return 'Hello, {} from {}!'.format(random.choice(["foo", "bar", "baz"]), os.getenv("APP_NAME", "Anon"))

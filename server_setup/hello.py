from flask import Flask
app = Flask(__name__)

import datetime
import os

@app.route('/')
def hello_world():
    template = """\
<h1>Hello, World!</h1>
<p>The time is {time}</p>
<p>Here is my config</p>
<ul>
  <li>APP_NAME={app_name}</li>
  <li>APP_VERSION={app_version}</li>
  <li>APP_SCALE={app_scale}</li>
</ul>
"""
    parameters = {
        "time": str(datetime.datetime.now()),
        "app_name": os.getenv("APP_NAME", "Unknown"),
        "app_version": os.getenv("APP_VERSION", "Unknown"),
        "app_scale": os.getenv("APP_SCALE", "Unknown")
    }

    return template.format(**parameters)

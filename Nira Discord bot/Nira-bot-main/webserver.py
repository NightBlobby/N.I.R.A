from flask import Flask
from threading import Thread
import logging

app = Flask('')


@app.route('/')
def home():
  return "I'm alive"


def run():
  # Suppress Flask/Werkzeug logging
  log = logging.getLogger('werkzeug')
  log.setLevel(
      logging.ERROR)  # Only log errors, suppressing info and warning logs

  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.start()

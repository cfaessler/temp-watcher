#!/bin/python
# -*- coding: utf-8 -*-

import datetime
import requests
import logging
from functools import wraps
from requests.exceptions import ConnectionError
from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO
from settings import SettingsWrapper

# Read settings
settings = SettingsWrapper()

PUSHOVER_URL = 'https://api.pushover.net/1/messages.json'
MONGODB_URL = 'mongodb://localhost:27017/'
DB = 'db'

# Logging setup
LOGGING_LEVEL = logging.DEBUG
LOGFILE = 'logging.log'
logging.basicConfig(filename=LOGFILE, level=LOGGING_LEVEL)
logger = logging.getLogger('WebServer')

# Flask and socketio setup
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.APP_KEY
socketio = SocketIO(app)
notified = False




def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == settings.USER and password == settings.PASSWORD

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Falsche Logindaten.\n'
    'Du hast hier nichts zu suchen!', 401,
    {'WWW-Authenticate': 'Basic realm="Login erforderlich"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated



def get_db():
    client = MongoClient(MONGODB_URL)
    return client[DB]


def get_latest_reading():
    latest = get_db().readings.find().sort([('date', -1)]).limit(1)
    return latest[0]


@socketio.on('connect')
def on_connect():
    logging.info('New client with IP {0} connected'.format(request.remote_addr))


@app.route('/add')
@requires_auth
def add_value():
    global notified
    value = float(request.args.get('value', ''))
    db = get_db()

    now = datetime.datetime.utcnow()
    reading = {"value": value,
               "date": now}
    db.readings.insert_one(reading)

    if value < settings.THRESHOLD and not notified:
        logging.info('Temperature under threshold, notifying user')
        message = 'Die Temperatur ist %s Grad und hat den Grenzwert unterschritten. Bitte Holz nachlegen!' % value

        data = {'token': settings.PUSHOVER_API_TOKEN,
                'user': settings.PUSHOVER_API_USER,
                'message': message}
        try:
            requests.post(PUSHOVER_URL, data)
        except ConnectionError:
            logging.error('Could not send push message due to connection error')
        else:
            notified = True

    if value > settings.THRESHOLD + settings.HYSTERESIS:
        notified = False
        logging.info('Resetting notification to not-notified')

    epoch = datetime.datetime(1970, 1, 1)
    timestamp = int((now - epoch).total_seconds()) * 1000

    data = {'date': timestamp, 'value': value}
    socketio.emit('newData', data, broadcast=True)
    return "success"


@app.route('/settings', methods=['POST', 'GET'])
@requires_auth
def config():
    saved = False
    if request.method == 'POST':
        settings.set('Pushover', 'API_TOKEN', request.form['API_TOKEN'])
        settings.set('Pushover', 'API_USER', request.form['API_USER'])
        settings.set('Global', 'THRESHOLD_DEGREES', request.form['THRESHOLD'])
        settings.set('Global', 'HYSTERESIS', request.form['HYSTERESIS'])
        settings.set('Global', 'INTERVAL', request.form['INTERVAL'])
        settings.update_settings()
        saved = True

    return render_template('config.htm',
                           API_TOKEN=settings.PUSHOVER_API_TOKEN,
                           API_USER=settings.PUSHOVER_API_USER,
                           THRESHOLD=settings.THRESHOLD,
                           HYSTERESIS=settings.HYSTERESIS, INTERVAL=settings.INTERVAL,
                           settings_saved=saved)


@app.route('/index')
@requires_auth
def index():
    return render_template('index.htm')


@app.route('/readings')
@requires_auth
def get_readings():
    db = get_db()
    data = dumps(db.readings.find().sort([('date', -1)]).limit(50))
    return Response(data, mimetype="application/json")


@app.route('/latest')
@requires_auth
def get_latest():
    return Response(get_latest_reading(), mimetype="application/json")


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)

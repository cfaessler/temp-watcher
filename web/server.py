#!/bin/python
# -*- coding: utf-8 -*-

import datetime
import ConfigParser
import requests
from requests.exceptions import ConnectionError
from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask, render_template, request, Response
import logging

# Config section
LOGGING_LEVEL = logging.DEBUG
LOGFILE = 'logging.log'

logging.basicConfig(filename=LOGFILE, level=LOGGING_LEVEL)
logger = logging.getLogger('TemperatureSensorReading')

MONGODB_URL = 'mongodb://localhost:27017/'
DB = 'db'

app = Flask(__name__)
notified = False

# Read settings
settings = ConfigParser.RawConfigParser()
settings.read('settings.cfg')
THRESHOLD = settings.getint('Global', 'THRESHOLD_DEGREES')
HYSTERESIS = settings.getint('Global', 'HYSTERESIS')
PUSH_API_TOKEN = settings.get('Pushover', 'API_TOKEN')
PUSH_API_USER = settings.get('Pushover', 'API_USER')


def get_db():
    client = MongoClient(MONGODB_URL)
    return client[DB]


@app.route('/add')
def add_value():
    value = request.args.get('value', '')
    db = get_db()
    reading = {"value": value,
               "date": datetime.datetime.utcnow()}
    db.readings.insert_one(reading)

    if value < THRESHOLD and not notified:
        logging.info('Temperature under threshold, notifying user')
        message = 'Die Temperatur ist %s Grad und hat den Grenzwert überschritten. Bitte Holz nachlegen!' % value
        url = 'https://api.pushover.net/1/messages.json'
        data = {'token': PUSH_API_TOKEN,
                'user': PUSH_API_USER,
                'message': message}
        try:
            requests.post(url, data)
        except ConnectionError:
            pass
        notified = True

    if value > THRESHOLD + HYSTERESIS:
        notified = False
        logging.info('Resetting notification to not-notified')
    return "success"


@app.route('/settings')
def config():
    return render_template('config.htm',
                           API_TOKEN=PUSH_API_TOKEN,
                           API_USER=PUSH_API_USER,
                           THRESHOLD=THRESHOLD,
                           HYSTERESIS=HYSTERESIS)


@app.route('/index')
def index():
    return render_template('index.htm')


@app.route('/readings')
def get_readings():
    db = get_db()
    data = dumps(db.readings.find().sort([('date', -1)]).limit(20))
    return Response(data, mimetype="application/json")


@app.route('/latest')
def get_latest():
    time = str(datetime.datetime.utcnow())
    latest = get_db().readings.find().sort([('date', -1)]).limit(1)
    data = dumps(latest)
    return Response(data, mimetype="application/json")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

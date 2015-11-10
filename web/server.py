#!/bin/python

import datetime
from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, Response
#from flask.json import dumps

MONGODB_URL = 'mongodb://localhost:27017/'
DB = 'db'

app = Flask(__name__)


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
    return "success"


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


    import random, time
    number = random.randint(1,20)
    timestamp = int(time.time())

    return Response(data, mimetype="application/json")
    return jsonify([timestamp, number])


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

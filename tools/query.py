from w1thermsensor import W1ThermSensor
import requests
from requests.exceptions import ConnectionError
import time
import logging

# Config section
LOGGING_LEVEL = logging.DEBUG
LOGFILE = 'logging.log'

logging.basicConfig(filename=LOGFILE, level=LOGGING_LEVEL)
logger = logging.getLogger('TemperatureSensorReading')

sensor = W1ThermSensor()
interval_secs = 1

while True:
    temp = sensor.get_temperature()
    logger.info("Temperature is %i" % temp)
    try:
        r = requests.get('http://localhost:5000/add?value=' + str(temp))
    except ConnectionError as e:
        logger.error("Could not connect to server")
    time.sleep(interval_secs)

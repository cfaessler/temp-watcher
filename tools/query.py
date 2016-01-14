from w1thermsensor import W1ThermSensor
import requests
import ConfigParser
from requests.exceptions import ConnectionError
import time
import logging

# Config section
LOGGING_LEVEL = logging.DEBUG
LOGFILE = 'logging.log'

logging.basicConfig(filename=LOGFILE, level=LOGGING_LEVEL)
logger = logging.getLogger('TemperatureSensorReading')

# Read settings
settings = ConfigParser.RawConfigParser()
settings.read('../settings.cfg')

sensor = W1ThermSensor()
INTERVAL_SECS = settings.getint('Global', 'INTERVAL')
WEB_SERVER = settings.get('Global', 'WEB_SERVER')

while True:
    temp = sensor.get_temperature()
    logger.info("Temperature is %i" % temp)
    try:
        r = requests.get('http://%s/add?value=%s' % (WEB_SERVER, temp), auth=(settings.get('Global','User'), settings.get('Global','Password')))
    except ConnectionError as e:
        logger.error("Could not connect to server")
    time.sleep(INTERVAL_SECS)

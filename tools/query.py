from w1thermsensor import W1ThermSensor
import requests
from requests.exceptions import ConnectionError 
import time
import logging

sensor = W1ThermSensor()

while True:
	
	temp=sensor.get_temperature()
	logging.info("Temperature is %i" % temp)	
	try:	
		r = requests.get('http://localhost:5000/add?value='+str(temp))
	except ConnectionError as e:
		logging.error("Could not connect to server")
	time.sleep(1)
	
	

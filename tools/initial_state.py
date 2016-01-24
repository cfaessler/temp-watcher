import time
from ISStreamer.Streamer import Streamer

streamer = Streamer(bucket_name="Stream Example", bucket_key="[Place A Unique Bucket Identifier Here]", access_key="[Place Your Access Key Here]")

streamer.log("By Messages", "Stream Starting")
for num in range(1, 20):
    time.sleep(0.1)
    streamer.log("My Numbers", num)
	if num%2 == 0:
        streamer.log("My Booleans", "false")
	else: 
        streamer.log("My Booleans", "true")
	if num%3 == 0:
        streamer.log("My Events", "pop")
	if num%10 == 0:
        streamer.log("My Messages", "Stream Half Done")
streamer.log("My Messages", "Stream Done")

import json
import time
from kafka import KafkaConsumer

KAFKA_URL = "localhost:9092"
MATCH_TOPIC = "ride-matches"

consumer = KafkaConsumer(
    MATCH_TOPIC,
    bootstrap_servers=KAFKA_URL
)

for message in consumer:
    ride = json.loads(message.value)
    user = ride["user"]
    driver = ride["driver"]

    print(f"{driver} is on the way to pick up {user}...")
    time.sleep(2)

    print(f"{user} is now in the car. Ride started...")
    time.sleep(3)

    print(f"{user} has arrived at {ride['destination']}. Ride completed!")

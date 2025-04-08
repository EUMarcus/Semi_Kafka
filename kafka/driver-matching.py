from kafka import KafkaConsumer, KafkaProducer
import json
import random

KAFKA_URL = "localhost:9092"
REQUEST_TOPIC = "ride-requests"
MATCH_TOPIC = "ride-matches"

drivers = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"}
]

consumer = KafkaConsumer(
    REQUEST_TOPIC,
    bootstrap_servers=KAFKA_URL
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_URL,
)

for message in consumer:
    ride_request = json.loads(message.value)
    assigned_driver = random.choice(drivers)

    ride_match = {
        "user": ride_request["user"],
        "pickup": ride_request["pickup"],
        "destination": ride_request["destination"],
        "driver": assigned_driver["name"]
    }

    print(f"Matched {ride_request['user']} with driver {assigned_driver['name']}")
    producer.send(MATCH_TOPIC, json.dumps(ride_match).encode())

import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaConsumer


app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-notification"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)



for message in consumer:
    currency_data = json.loads(message.value)

    user = currency_data.get("user")
    base = currency_data.get("baseCurrency")
    sBase = currency_data.get("sBaseCurrency")
    sTarget = currency_data.get("sTargetCurrency")

    if user:
        print(user,"requests to view exchange rates with the base currency of", base)
    else:
        print("User is searching for", sTarget, "currency with the base currency of",  sBase)








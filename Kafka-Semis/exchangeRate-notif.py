import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaConsumer
from datetime import datetime
from fastapi.staticfiles import StaticFiles

app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-activity"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)



for message in consumer:
    currency_data = json.loads(message.value)
    user = currency_data.get("user")
    newUser = currency_data.get("newUser")
    base = currency_data.get("baseCurrency")
    sBase = currency_data.get("sBaseCurrency")
    sTarget = currency_data.get("sTargetCurrency")
    amount = currency_data.get("amount")

    if user:
        print(user,"requests to view exchange rates with the base currency of", base)
    elif amount:
        print("User is converting", amount, "with the base currency of",sBase," with the target currency of",  sTarget)
    elif newUser:
        now = datetime.now()
        print(newUser,"logged in at", now)
    else:
        print("User is searching for", sTarget, "currency with the base currency of",  sBase)








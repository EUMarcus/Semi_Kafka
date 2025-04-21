# import json
# from fastapi import FastAPI, BackgroundTasks
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from kafka import KafkaConsumer
# from starlette.requests import Request
# from fastapi.staticfiles import StaticFiles
# import threading

import json, threading
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from kafka import KafkaConsumer
from starlette.requests import Request


# FastAPI setup
app = FastAPI()


templates = Jinja2Templates(directory="templates")


KAFKA_URL = "localhost:9092"
TOPIC = "profile-information"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)

for message in consumer:
    profile_data = json.loads(message.value)
    user = profile_data.get("username")
    newUser = profile_data.get("email")
    base = profile_data.get("password")
    sBase = profile_data.get("balance")
    sTarget = profile_data.get("currency")

    print(profile_data)
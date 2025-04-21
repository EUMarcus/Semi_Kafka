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



# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-activity"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL,
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

exchange_data_list = []


def consume_kafka_messages():
    for message in consumer:
        currency_data = json.loads(message.value)
        user = currency_data.get("user")
        base = currency_data.get("baseCurrency")
        sBase = currency_data.get("sBaseCurrency")
        sTarget = currency_data.get("sTargetCurrency")

        exchange_data_list.append({
            "user": user,
            "base": base,
            "sBase": sBase,
            "sTarget": sTarget
        })

# Start Kafka consumer once on startup
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=consume_kafka_messages, daemon=True)
    thread.start()


@app.get("/", response_class=HTMLResponse)
async def get_exchange_rate(request: Request, background_tasks: BackgroundTasks):
    # background_tasks.add_task(consume_kafka_messages)
    # Only show the last 25 entries (most recent)
    latest_data = exchange_data_list[-25:][::-1]

    cleaned_data = [ {key: value for key, value in entry.items() if value is not None} for entry in latest_data]

    return templates.TemplateResponse("currency_notif.html", {
        "request": request,
        "exchange_data_list": cleaned_data
    })



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5007)
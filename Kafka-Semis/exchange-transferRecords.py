import json, threading
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from kafka import KafkaConsumer, KafkaProducer
from starlette.requests import Request
from tinydb import Query, TinyDB


# FastAPI setup
app = FastAPI()




# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

userDB = TinyDB('users.json')
users = userDB.table('users')
User = Query()

balanceDB = TinyDB('balance.json')
balances = balanceDB.table('balance')
Balance = Query()

KAFKA_URL = "localhost:9092"
TOPIC = "money-transfer-records"
TOPIC_2 = "balance_updates"

producer = KafkaProducer(
    bootstrap_servers = KAFKA_URL
)

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)

transfer_data_list = []


def consume_kafka_messages():
    for message in consumer:
        transfer_data = json.loads(message.value)
        senderData = balances.get(Balance.username == transfer_data.get("userSender"))
        receiverData = balances.get(Balance.username == transfer_data.get("userReceiver"))
        sentAmount = transfer_data.get("sentAmount")
        converted_amount = transfer_data.get("converted_amount")

        transfer_data_list.append({
                "user": senderData["username"],
                "userCurrency": senderData["currency"],
                "receiver": receiverData["username"],
                "amount": sentAmount,
                "receiverCurrency": receiverData["currency"],
                "convertedAmount": converted_amount
            })
    
        producer.send(TOPIC_2, json.dumps(transfer_data_list).encode())


# Start Kafka consumer once on startup
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=consume_kafka_messages, daemon=True)
    thread.start()


@app.get("/", response_class=HTMLResponse)
async def get_exchange_rate(request: Request, background_tasks: BackgroundTasks):
    # background_tasks.add_task(consume_kafka_messages)
    # Only show the last 25 entries (most recent)
    latest_data = transfer_data_list[-25:][::-1]

    cleaned_data = [ {key: value for key, value in entry.items() if value is not None} for entry in latest_data]

    return templates.TemplateResponse("currency_sending.html", {
        "request": request,
        "transfer_data_list": cleaned_data
    })



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5006)

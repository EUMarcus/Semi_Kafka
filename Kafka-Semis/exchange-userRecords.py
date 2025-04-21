# import json,threading
# from fastapi import FastAPI
# from fastapi import BackgroundTasks, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from kafka import KafkaConsumer
# from tinydb import TinyDB, Query

import json
import threading
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaConsumer
from tinydb import Query, TinyDB
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

userDB = TinyDB('users.json')
users = userDB.table('users')
User = Query()

balanceDB = TinyDB('balance.json')
balances = balanceDB.table('balance')
Balance = Query()

KAFKA_URL = "localhost:9092"
TOPIC = "user-data-records"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)

user_data_list = []

def consume_kafka_messages():
    for message in consumer:
        user_data = json.loads(message.value)
        data = users.get(User.username == user_data.get("username"))
        fdata =  balances.get(Balance.username == user_data.get("username"))
        del fdata['username']
        
        print(message)


        merged_data = {**data, **fdata}

        user_data_list.append(merged_data)



# Start Kafka consumer once on startup
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=consume_kafka_messages, daemon=True)
    thread.start()


@app.get("/", response_class=HTMLResponse)
async def get_user_accounts(request: Request, background_tasks: BackgroundTasks):
    # background_tasks.add_task(consume_kafka_messages)
    # Only show the last 25 entries (most recent)
    latest_data = user_data_list[-25:][::-1]

    cleaned_data = [ {key: value for key, value in entry.items() if value is not None} for entry in latest_data]

    return templates.TemplateResponse("currency_accounts.html", {
        "request": request,
        "user_data_list": cleaned_data
    })



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5005)




import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaProducer
from fastapi import Request

app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "ride-requests"

producer = KafkaProducer(bootstrap_servers=KAFKA_URL)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def display_home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
def request_ride(user: str, baseCurrency: str, targetCurrrency: str):
    data = {"user": user, "baseCurrency": baseCurrency, "targetCurrrency" : targetCurrrency}
    print("Base Currency Change Detected:", data)

    # Send to Kafka
    producer.send(TOPIC, json.dumps(data).encode())

    return {"message": "Base Currency Changed Successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)   

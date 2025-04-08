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

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def display_home_page(request: Request):
    # Render the HTML template (index.html) with any context
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/rides")
def request_ride(user: str, pickup: str, destination: str):
    data = {"user": user, "pickup": pickup, "destination": destination}
    print("Ride Request Detected:", data)

    # Send to Kafka
    producer.send(TOPIC, json.dumps(data).encode())

    return {"message": "Ride requested successfully!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)

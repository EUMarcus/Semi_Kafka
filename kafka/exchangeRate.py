import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaProducer



# FastAPI setup
app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-notification"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_URL
)


templates = Jinja2Templates(directory="templates")

# Handling the POST request when the user submits the form
@app.post("/", response_class=HTMLResponse)
async def setCurrency(
    request: Request,
    user: str = Form(...),
    baseCurrency: str = Form(...)
):
    # Create a dictionary to hold the user-submitted data
    data = {"user": user, "baseCurrency": baseCurrency}
    print("Base Currency Change Detected:", data)
    
    # Send the data to Kafka for tracking
    producer.send(TOPIC, json.dumps(data).encode())
    
   
    return templates.TemplateResponse("currency_view.html", {
        "request": request,
        "message": "Base Currency Changed Successfully!",
        "user": user,
        "base_currency": baseCurrency,
        
    })


@app.get("/", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    return templates.TemplateResponse("currency_view.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)   

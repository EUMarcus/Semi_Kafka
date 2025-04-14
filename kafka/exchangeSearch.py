from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests, json
from kafka import KafkaProducer
from fastapi.templating import Jinja2Templates


app = FastAPI()

# Kafka Config
KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-notification"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Exchange Rate API
EXCHANGE_API_KEY = "9182c69d6189cb61ba450f03"
EXCHANGE_API_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair"

templates = Jinja2Templates(directory="templates")

@app.post("/", response_class=HTMLResponse)
async def searchCurrency(
    request: Request,
    baseCurrency: str = Form(...),
    targetCurrency: str = Form(...)
):
    # Create a dictionary to hold the user-submitted data
    data = {"sBaseCurrency": baseCurrency,"sTargetCurrency": targetCurrency}
    print("User searching for a specific currency", data)
    
    # Send the data to Kafka for tracking
    producer.send(TOPIC, data)
    
   
    return templates.TemplateResponse("currency_search.html", {
        "request": request,
        "message": "Search for Currency Successfull!",
        "base_currency": baseCurrency,
        "target_currency": targetCurrency
        
    })


@app.get("/", response_class=HTMLResponse)
async def getSearchPage(request: Request):
    return templates.TemplateResponse("currency_search.html", {"request": request})




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001)   

from fastapi import FastAPI, Query
from pydantic import BaseModel
import requests, json
from kafka import KafkaProducer

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

class SearchResult(BaseModel):
    base: str
    target: str
    rate: float

@app.get("/search", response_model=SearchResult)
def get_conversion_rate(
    base: str = Query(..., min_length=3, max_length=3),
    target: str = Query(..., min_length=3, max_length=3)
):
    base = base.upper()
    target = target.upper()
    url = f"{EXCHANGE_API_URL}/{base}/{target}"
    response = requests.get(url)
    data = response.json()

    if data["result"] != "success":
        rate = 0.0
    else:
        rate = data["conversion_rate"]

    # Kafka log
    message = {
        "base": base,
        "target": target,
        "rate": rate
    }
    producer.send(TOPIC, message)
    producer.flush()

    return message


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001)   

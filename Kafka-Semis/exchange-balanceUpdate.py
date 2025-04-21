import json
from fastapi import FastAPI

from kafka import KafkaConsumer

from tinydb import TinyDB, Query

app = FastAPI()

userDB = TinyDB('users.json')
users = userDB.table('users')
User = Query()

balanceDB = TinyDB('balance.json')
balances = balanceDB.table('balance')
Balance = Query()

KAFKA_URL = "localhost:9092"
TOPIC = "balance_updates"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)

for message in consumer:
    balance_data = json.loads(message.value)

    # Loop through each transaction in the list
    for data in balance_data:
        sender = data.get("user")
        senderCurrency = data.get("userCurrency")
        receiver = data.get("receiver")
        receiverCurrency = data.get("receiverCurrency")
        amount = data.get("amount")
        convertedAmount = data.get("convertedAmount")


        senderData = balances.get(Balance.username == sender)
        receiverData = balances.get(Balance.username == receiver)


        # Update sender balance
        new_sBalance = senderData['balance'] - amount
        balances.update({"balance": new_sBalance}, User.username == sender)

        # Update receiver balance
        new_Balance = receiverData['balance'] + convertedAmount
        balances.update({"balance": new_Balance}, Balance.username == receiver)

        print(sender, senderCurrency, receiver, receiverCurrency, amount, convertedAmount)





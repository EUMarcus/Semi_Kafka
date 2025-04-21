import json, requests
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaProducer, KafkaConsumer
from tinydb import TinyDB, Query
from fastapi.staticfiles import StaticFiles

app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-activity"
TOPIC_2 = "profile-information"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_URL
)

# profile_consumer = KafkaConsumer(
#     TOPIC_2,
#     bootstrap_servers = KAFKA_URL
# )


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name='static')

userLoggedIn = ""
userInfo = {}

@app.post("/viewCurrency", response_class=HTMLResponse)
async def setCurrency(
    request: Request,
    user: str = Form(...),
    baseCurrency: str = Form(...)
):
  
    data = {"user": user, "baseCurrency": baseCurrency}
    print(userLoggedIn)
    print("Base Currency Change Detected:", data)
    

    producer.send(TOPIC, json.dumps(data).encode())
    
   
    return templates.TemplateResponse("currency_view.html", {
        "request": request,
        "message": "Base Currency Changed Successfully!",
        "user": user,
        "base_currency": baseCurrency,
        
    })

@app.get("/viewCurrency", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    return templates.TemplateResponse("currency_view.html", {"request": request})

@app.post("/searchCurrency", response_class=HTMLResponse)
async def searchCurrency(
    request: Request,
    baseCurrency: str = Form(...),
    targetCurrency: str = Form(...)
):
    # Create a dictionary to hold the user-submitted data
    data = {"sBaseCurrency": baseCurrency,"sTargetCurrency": targetCurrency}
    print("User searching for a specific currency", data)
    
    # Send the data to Kafka for tracking
    producer.send(TOPIC, json.dumps(data).encode())
    
   
    return templates.TemplateResponse("currency_search.html", {
        "request": request,
        "message": "Search for Currency Successfull!",
        "base_currency": baseCurrency,
        "target_currency": targetCurrency
        
    })


@app.get("/searchCurrency", response_class=HTMLResponse)
async def getSearchPage(request: Request):
    return templates.TemplateResponse("currency_search.html", {"request": request})


@app.post("/convertCurrency", response_class=HTMLResponse)
async def searchCurrency(
    request: Request,
    baseCurrency: str = Form(...),
    targetCurrency: str = Form(...),
    baseAmount: int = Form(...)
):
    data = {"sBaseCurrency": baseCurrency,"sTargetCurrency": targetCurrency,"amount": baseAmount}
    print("User is converting",baseAmount, baseCurrency, "into", targetCurrency)
    
    producer.send(TOPIC, json.dumps(data).encode())
    
   
    return templates.TemplateResponse("currency_convert.html", {
        "request": request,
        "message": "Search for Currency Successfull!",
        "base_currency": baseCurrency,
        "target_currency": targetCurrency,
        "base_amount": baseAmount
    })


@app.get("/convertCurrency", response_class=HTMLResponse)
async def getSearchPage(request: Request):
    return templates.TemplateResponse("currency_convert.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    return templates.TemplateResponse("currency_landing.html", {"request": request})


@app.get("/", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    return templates.TemplateResponse("currency_mainpage.html", {"request": request})





# Profile View
@app.get("/viewProfile", response_class=HTMLResponse)
async def getProfilePage(request: Request):
    global userInfo

    data = {
    "request": request,
    "username": userInfo['username'],
    "email": userInfo['email'],
    "password": userInfo['password'],
    "balance": userInfo['balance'],
    "currency": userInfo['currency'],
}

    if 'notification' in userInfo and userInfo['notification']:
        data["notification"] = userInfo["notification"]

        amount = balances.get(Balance.username == userInfo['username'])
        if amount and 'notification' in amount:
            del amount['notification']
            balances.remove(Balance.username == userInfo['username'])
            balances.insert(amount)
        del userInfo['notification'] 

    return templates.TemplateResponse("currency_profileView.html", data)


@app.post("/viewProfile", response_class=HTMLResponse)
async def sendMoney(
    request: Request,
    userSent: str = Form(...),
    sentAmount: float = Form(...)
    ):
    global userInfo

    if userSent == userInfo['username']:
        return HTMLResponse("User cannot be your own account", status_code=400)
    receiver_data = balances.get(Balance.username == userSent)
    if not receiver_data:
        return HTMLResponse("Receiver not valid.", status_code=404)

    baseCurrency = userInfo['currency']
    targetCurrency = receiver_data['currency']

    if sentAmount <= userInfo['balance']:
        newAmount = userInfo['balance'] - sentAmount
        userInfo['balance'] = newAmount

        users.update({"balance": newAmount}, User.username == userInfo['username'])

        apiUrl = f"https://v6.exchangerate-api.com/v6/9182c69d6189cb61ba450f03/pair/{baseCurrency}/{targetCurrency}/{sentAmount}"
        response = requests.get(apiUrl)
        data = response.json()
        print(data['conversion_result'])
        if data['result'] != "success":
            return HTMLResponse("Conversion failed.", status_code=500)

        converted_Sent = data['conversion_result']
        new_Balance = receiver_data['balance'] + converted_Sent

        balances.update({"balance": new_Balance}, Balance.username == userSent)
        balances.update({"notification": f"{userInfo['username']} has sent you {sentAmount} in {baseCurrency}. Which is {data['conversion_result']} when converted to your currency."}, User.username == userSent)
        return templates.TemplateResponse("currency_profileView.html", {
            "request": request,
            "username": userInfo['username'],
            "email": userInfo['email'],
            "password": userInfo['password'],
            "balance": userInfo['balance'],
            "currency": userInfo['currency'],
            "message": f"Successfully sent {sentAmount} {baseCurrency} to {userSent}"
        })

    return HTMLResponse("Insufficient balance.", status_code=400)
        











# Users Side

userDB = TinyDB('users.json')
users = userDB.table('users')
User = Query()


balanceDB = TinyDB('balance.json')
balances = balanceDB.table('balance')
Balance = Query()

def signup(username, email, password, balance, currency):
    if users.search(User.username == username) or balance < 0:
        return False
    users.insert({'username': username, 'email': email, 'password': password})
    balances.insert({'username': username, 'balance': balance, "currency": currency})
    return True

def login(username, password):
    user = users.get(User.username == username)
    if user and user['password'] == password:
        return True
    return False

@app.get("/currencySignup", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    return templates.TemplateResponse("currency_signup.html", {"request": request})

@app.post("/currencySignup", response_class=HTMLResponse)
async def getUserCreds(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    balance: float = Form(...),
    baseCurrency: str = Form(...)
):
    response = signup(username, email, password, balance, baseCurrency)
    if response:
        data = {"username": username,"email": email,"password": password}
        print("New user added! Welcome", username)
        
        # ala pa papagsendan na topic
        # producer.send(TOPIC, json.dumps(data).encode())

        return RedirectResponse(url="/currencyLogin", status_code=303)

    else:
        if balance < 0:
            print("Balance cannot be less than 0")
        else:
            print("Username already taken")
        return templates.TemplateResponse("currency_error.html", {"request": request})

@app.get("/currencyLogin", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    return templates.TemplateResponse("currency_login.html", {"request": request})






@app.post("/currencyLogin", response_class=HTMLResponse)
async def loginUser(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    
    response = login(username, password)
    
    if response:
        data = {"newUser": username}
        print("User Logged In, Welcome", username,"!")
        
        user_data = users.get(User.username == username)
        financial_data =  balances.get(Balance.username == username)
        del financial_data['username']
        
        
        merged_data = {**user_data, **financial_data}
        
        producer.send(TOPIC_2, json.dumps(merged_data).encode())
        producer.send(TOPIC, json.dumps(data).encode())
        

        global userLoggedIn
        userLoggedIn = username
        global userInfo
        userInfo = merged_data
        
        return RedirectResponse(url="/home",status_code=303)
    else:
        print("Invalid login credentials.")
    

        return templates.TemplateResponse("currency_error.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)   

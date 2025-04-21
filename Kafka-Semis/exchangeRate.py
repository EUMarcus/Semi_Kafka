import json, requests
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaProducer, KafkaConsumer
from tinydb import TinyDB, Query
from fastapi.staticfiles import StaticFiles

app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-activity"
TOPIC_2 = "money-transfer-records"
TOPIC_3 = "user-data-records"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_URL
)




templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name='static')

userLoggedIn = ""
userInfo = {}

@app.post("/viewCurrency", response_class=HTMLResponse)
async def setCurrency(
    request: Request,
    baseCurrency: str = Form(...)
):
    global userLoggedIn
    data = {"user": userLoggedIn, "baseCurrency": baseCurrency}
    print(userLoggedIn)
    print("Base Currency Change Detected:", data)
    

    producer.send(TOPIC, json.dumps(data).encode())
    
   
    return templates.TemplateResponse("currency_view.html", {
        "request": request,
        "message": "Base Currency Changed Successfully!",
        "user": userLoggedIn,
        "base_currency": baseCurrency,
        
    })

@app.get("/viewCurrency", response_class=HTMLResponse)
async def getCurrencyPage(request: Request):
    global userLoggedIn
    return templates.TemplateResponse("currency_view.html", {
        "request": request,
        "welcome_message": f"Hello {userLoggedIn}!Welcome to curEx, your one stop shop for your currency exchanging needs!"
        })

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
async def convertCurrency(
    request: Request,
    baseCurrency: str = Form(...),
    targetCurrency: str = Form(...),
    baseAmount: str = Form(...)
):

    try:
        bamount = float(baseAmount)
    except:
        print("Base amount must be a valid float.")
        return templates.TemplateResponse ("currency_error.html",{"request": request})
    if bamount <= 0:
        print("Base amount must be a positive integer greater than zero.")
        return templates.TemplateResponse ("currency_error.html",{"request": request})


            
        

    data = {"sBaseCurrency": baseCurrency,"sTargetCurrency": targetCurrency,"amount": bamount}
    print("User is converting",bamount, baseCurrency, "into", targetCurrency)
    
    producer.send(TOPIC, json.dumps(data).encode())
    
   
    return templates.TemplateResponse("currency_convert.html", {
        "request": request,
        "message": "Search for Currency Successfull!",
        "base_currency": baseCurrency,
        "target_currency": targetCurrency,
        "base_amount": bamount
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

    request_for_tempalate = {
        "request": request,
        "username": userInfo['username'],
        "email": userInfo['email'],
        "balance": userInfo['balance'],
        "currency": userInfo['currency'],
    }

    receiver_data = balances.get(Balance.username == userSent)
    
    if userSent == userInfo['username']:
        request_for_tempalate['error'] = "You cannot send money to your own account."
        return templates.TemplateResponse("currency_profileView.html", request_for_tempalate)
    elif sentAmount <= 0:
        request_for_tempalate['error'] = "Amount must be greater than 0."
        return templates.TemplateResponse("currency_profileView.html", request_for_tempalate)
    elif not receiver_data:
        request_for_tempalate['error'] = "Receiver not found."
        return templates.TemplateResponse("currency_profileView.html", request_for_tempalate)
    elif sentAmount > userInfo['balance']:
        request_for_tempalate['error'] = "Insufficient balance."
        return templates.TemplateResponse("currency_profileView.html", request_for_tempalate)
    else:
    # Proceed with conversion and update
        baseCurrency = userInfo['currency']
        targetCurrency = receiver_data['currency']
        EXCHANGE_API_KEY = "9182c69d6189cb61ba450f03"
        apiUrl = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{baseCurrency}/{targetCurrency}/{sentAmount}"

        try:
            response = requests.get(apiUrl)
            data = response.json()

            if data.get('result') != "success":
                return templates.TemplateResponse("currency_profileView.html", {
                    "request": request,
                    "username": userInfo['username'],
                    "email": userInfo['email'],
                    "balance": userInfo['balance'],
                    "currency": userInfo['currency'],
                    "error": "Currency conversion failed."
                })

            converted_Sent = data['conversion_result']

            # # Update sender balance
            # userInfo['balance'] -= sentAmount
            # balances.update({"balance": userInfo['balance']}, User.username == userInfo['username'])

            # # Update receiver balance
            # new_Balance = receiver_data['balance'] + converted_Sent
            # balances.update({"balance": new_Balance}, Balance.username == userSent)

            # Add notification to receiver
            balances.update({
                "notification": f"{userInfo['username']} sent you {sentAmount} {baseCurrency} ({converted_Sent} {targetCurrency})"
            }, Balance.username == userSent)

            transfer_data =  {
                "userSender": userInfo['username'],
                "userReceiver": userSent,
                "sentAmount": sentAmount,
                "converted_amount": converted_Sent
            }

            producer.send(TOPIC_2, json.dumps(transfer_data).encode())

            return templates.TemplateResponse("currency_profileView.html", {
                "request": request,
                "username": userInfo['username'],
                "email": userInfo['email'],
                "password": userInfo['password'],
                "balance": userInfo['balance'],
                "currency": userInfo['currency'],
                "message": f"Successfully sent {sentAmount} {baseCurrency} to {userSent}."
            })




        except Exception as e:
            print("Transfer Error:", e)
            return templates.TemplateResponse("currency_profileView.html", {
                "request": request,
                "username": userInfo['username'],
                "email": userInfo['email'],
                "balance": userInfo['balance'],
                "currency": userInfo['currency'],
                "error": "Something went wrong during the transfer."
            })










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
        data = {"username": username}
        print("New user added! Welcome", username)
        

        producer.send(TOPIC_3, json.dumps(data).encode())

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

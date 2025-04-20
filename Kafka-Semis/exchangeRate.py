import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaProducer
from tinydb import TinyDB, Query
from fastapi.staticfiles import StaticFiles

app = FastAPI()

KAFKA_URL = "localhost:9092"
TOPIC = "exchange-rate-activity"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_URL
)


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name='static')

userLoggedIn = ""

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












# Users Side

userDB = TinyDB('users.json')
users = userDB.table('users')
User = Query()

def signup(username, password):
    if users.search(User.username == username):
        return False
    users.insert({'username': username, 'password': password})
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
    password: str = Form(...)
):
    response = signup(username, password)
    if response:
        data = {"username": username,"email": email,"password": password}
        print("New user added! Welcome", username)
        
        # ala pa papagsendan na topic
        # producer.send(TOPIC, json.dumps(data).encode())

        return RedirectResponse(url="/currencyLogin", status_code=303)

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
        
        producer.send(TOPIC, json.dumps(data).encode())
        global userLoggedIn
        userLoggedIn = username
        
        return RedirectResponse(url="/home",status_code=303)
    else:
        print("Invalid login credentials.")
    

        return templates.TemplateResponse("currency_error.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)   

"""
Routes and views for the flask application.
"""

from datetime import datetime
from TradingViewInteractiveBrokers import app
from sanic import Sanic
from sanic import response
import asyncio
import ast
import datetime
from ib_insync import *
# Create Sanicobject called app.
app = Sanic(__name__)
app.ib = None

# Create root to easily let us know its on/working.
@app.route('/')
async def root(request):
    return response.text('online')

#Check every minute if we need to reconnect to IB
async def checkIfReconnect():
    print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " Checking if we need to reconnect")
    #Reconnect if needed
    if not app.ib.isConnected() or not app.ib.client.isConnected():
        try:
            print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " Reconnecting")
            app.ib.disconnect()
            app.ib = IB()
            app.ib.connect('127.0.0.1', 7496, clientId=1)
            app.ib.errorEvent += onError
            print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " Reconnect Success")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print("Make sure TWS or Gateway is open with the correct port")
            print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " : " + str(e))
    return ''
@app.route('/webhook', methods=['POST'])
async def webhook(request):
    print(request)
    if request.method == 'POST':
        #Check if we need to reconnect with IB
        await checkIfReconnect()
        # Parse the string data from tradingview into a python dict
        data = request.json
        order = MarketOrder("BUY",1,account=app.ib.wrapper.accounts[0])
        print(data['symbol'])
        print(data['symbol'][0:3])
        print(data['symbol'][3:6])
        #contract = Crypto(data['symbol'][0:3],'PAXOS',data['symbol'][3:6]) #Get first 3 chars BTC then last 3 for currency USD
        #or stock for example 
        contract = Stock('SPY','SMART','USD')
        print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " Buying: "+ str(data['symbol']))
        app.ib.placeOrder(contract, order)        
    return response.json({})
#On IB Error
def onError(self,reqId, errorCode, errorString, contract):
    print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " : " + str(errorCode))
    print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " : " + str(errorString))
if __name__ == '__main__':
    #IB Connection
    #Connect to IB on init
    app.ib = IB()
    print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " Connecting to IB")
    app.ib.connect('127.0.0.1', 7496, clientId=1)
    print((datetime.datetime.now().strftime("%b %d %H:%M:%S")) + " Successfully Connected to IB")
    app.ib.errorEvent += onError
    app.run(port=5000)

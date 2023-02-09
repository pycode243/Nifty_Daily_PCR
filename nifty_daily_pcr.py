import yfinance as yf
import pandas as pd
import requests
import datetime
import mplfinance as mpf
from datetime import timedelta
import bokeh
from math import pi
from bokeh.plotting import figure
from bokeh.io import output_notebook,show
from bokeh.resources import INLINE
from bokeh.layouts import column

data = yf.download("^NSEI", start="2023-02-01", end="2023-02-09")
#data.to_csv("NIFTY_Daily_Record.csv", mode='a', index=True, header=False)
today = datetime.date.today()
yesterday = today - timedelta(days = 1)

sym = "NIFTY"
url = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + sym
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9'
}

session = requests.Session()
request = session.get(url, headers=headers)
cookies = dict(request.cookies)
response = session.get(url, headers=headers, cookies=cookies).json()
rawdata = pd.DataFrame(response)
rawop = pd.DataFrame(rawdata['filtered']['data']).fillna(0)

def dataframe(rawop):
    data = []
    for i in range(0, len(rawop)):
        calloi = calloi = cltp = putoi = putcoi = pltp = 0
        stp = rawop['strikePrice'][i]
        if (rawop['CE'][i] == 0):
            calloi = callcoi = 0
        else:
            calloi = rawop['CE'][i]['openInterest']
            callcoi = rawop['CE'][i]['changeinOpenInterest']
            cltp = rawop['CE'][i]['lastPrice']

        if (rawop['PE'][i] == 0):
            putoi = putcoi = 0
        else:
            putoi = rawop['PE'][i]['openInterest']
            putcoi = rawop['PE'][i]['changeinOpenInterest']
            pltp = rawop['PE'][i]['lastPrice']

        opdata = {
            'CALL OI': calloi, 'CALL CHNG OI': callcoi, 'CALL LTP': cltp, 'STRIKE PRICE': stp,
            'PUT LTP': pltp, 'PUT CHNG OI': putcoi, 'PUT OI': putoi
        }
        data.append(opdata)
    optionchain = pd.DataFrame(data)
    return optionchain
optionchain = dataframe(rawop)

try:
    nifty_df = yf.download("^NSEI", start=yesterday, end=today)
    TotalCallOI = optionchain['CALL OI'].sum()
    TotalPutOI = optionchain['PUT OI'].sum()
    print(f'Total Call OI:{TotalCallOI}: Total PUT OI:{TotalPutOI}')
    print(f'OI DIFF:{TotalPutOI - TotalCallOI}')
    PCR = (TotalPutOI / TotalCallOI).round(2)
    nifty_df["PCR"] = PCR
    #nifty_df.to_csv("NIFTY_PCR_Record.csv", mode='a', index=True, header=False)
except Exception as e:
    print("Oops! error in",e)

output_notebook(resources=INLINE)
inc = nifty_df.Close > nifty_df.Open
dec = nifty_df.Open > nifty_df.Close

w = 12*60*60*1000

## Candlestick chart
candlestick = figure(x_axis_type="datetime", title = "Nifty Daily Chart")

candlestick.segment(nifty_df.index, nifty_df.High, nifty_df.index, nifty_df.Low, color="black")

candlestick.vbar(nifty_df.index[inc], w, nifty_df.Open[inc], nifty_df.Close[inc],
         fill_color="lawngreen", line_color="red")

candlestick.vbar(nifty_df.index[dec], w, nifty_df.Open[dec], nifty_df.Close[dec],
         fill_color="tomato", line_color="lime")

## Volume Chart
volume = figure(x_axis_type= "datetime")

volume.vbar(nifty_df.index, width=w, top=nifty_df.PCR,
            fill_color="dodgerblue", line_color="tomato", alpha=0.8)


volume.xaxis.axis_label="Date"
volume.yaxis.axis_label="Put Call Ratio"
candlestick.yaxis.axis_label="Price"

show(column(candlestick, volume))
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import pandas as pd
from io import StringIO
import requests
from bs4 import BeautifulSoup
from  datetime import datetime , timedelta
import bs4
import numpy as np
import time
import copy
import re

def home(request):
    return render(request, "/Users/satyam/Desktop/Projects/ACM/acmsite/myapp/templates/base.html")

def rank_up(df):
    df = copy.deepcopy(df)
    df["CAGR2 Rank"] = df["cagr2"].rank(ascending=True)
    df["CAGR5 Rank"] = df["cagr5"].rank(ascending=True)
    df["Sharpe Rank"] = df["sharpe"].rank(ascending=True)
    df["Alpha Rank"] = df["alpha"].rank(ascending=True)
    df["Treynor Rank"] = df["treynor"].rank(ascending=True)
    df["Weighted Score"] = (
        0.35 * df["CAGR2 Rank"]
        + 0.25 * df["CAGR5 Rank"]
        + 0.20 * df["Sharpe Rank"]
        + 0.10 * df["Alpha Rank"]
        + 0.10 * df["Treynor Rank"]
    )

    df["Rank"] = df["Weighted Score"].rank(ascending=False)
    df = df.sort_values(by="Rank")
    return df

def mutual_funds(request):
     if request.method == 'POST':
        risk_bearing_capability = request.POST.get('mf_rbc', '')
        mf = pd.read_csv("/Users/satyam/Desktop/Projects/ACM/GPT-Fund/mf_saved.csv")
        low = mf.loc[(mf['beta'] < 0.9)]
        mod = mf.loc[(mf['beta'] > 0.9) & (mf['beta'] < 1)]
        high = mf.loc[(mf['beta'] > 1)]

        if risk_bearing_capability == "High":
            ret = rank_up(high)
            rdict = {}
            for i in range(3):
                rdict[ret.iloc[i]['mf']] = ret.iloc[i]['Weighted Score']
        
        if risk_bearing_capability == "Moderate":
            ret = rank_up(mod)
            rdict = {}
            for i in range(3):
                rdict[ret.iloc[i]['mf']] = ret.iloc[i]['Weighted Score']
        
        elif risk_bearing_capability == "Low":
            ret = rank_up(low)
            rdict = {}
            for i in range(3):
                rdict[ret.iloc[i]['mf']] = ret.iloc[i]['Weighted Score']

        return render(request, 'mutual_funds.html', {'risk_bearing_capability': risk_bearing_capability, 'rankings': rdict})

     return render(request, "/Users/satyam/Desktop/Projects/ACM/acmsite/myapp/templates/mutual_funds.html")

def number_of_stocks(amt, price):
    buy = [0 for j in range(len(price))]
    i = 0
    while amt>price[0]:
        if amt > price[i]:
            buy[i] += 1
            amt = amt - price[i]
        i = (i+1)%len(price)
    return buy

def get_price(ticker):
    url = f'https://www.tickertape.in/stocks/{ticker}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    class1 = "jsx-3168773259 current-price typography-h1 text-primary"
    price = soup.find(class_ = class1).text
    price = price.replace(",", "")
    price = price.split('.')
    ret = int(price[0]) + int(price[1])/(10**len(price[1]))
    return ret

def stocks(request):
    if request.method == 'POST':
        amount_to_invest = int(request.POST.get('amount_to_invest', 0))
        risk_bearing_capability = request.POST.get('risk_bearing_capability', '')

        stocks = pd.read_csv("/Users/satyam/Desktop/Projects/ACM/GPT-Fund/stocks_saved.csv")
        names = pd.read_csv("/Users/satyam/Desktop/Projects/ACM/GPT-Fund/tick_final.csv")

        high = stocks.loc[(stocks['Risk'] == 2) | (stocks['Value'] > 7)]
        high_sorted = high.sort_values(by='Value',  ascending=False)
        mod = stocks.loc[(stocks['Risk'] == 1) & (stocks['Value'] < 7)]
        mod_sorted = mod.sort_values(by='Value',  ascending=False)
        low = stocks.loc[(stocks['Risk'] == 0) & (stocks['Value'] < 7)]
        low_sorted = low.sort_values(by='Value',  ascending=False)

        if risk_bearing_capability == "High":
            price_list = []
            stb = []
            tick_list = []
            num = 0
            while num < 2:
                if high_sorted.iloc[num]['Price'] < amount_to_invest:
                    price_list.append(high_sorted.iloc[num]['Price'])
                    tick = high_sorted.iloc[num]["Stock"]
                    stb.append(names.loc[names['tt'] == tick, 'stock'].values[0])
                    tick_list.append(tick)
                    num = num + 1
            
            numstocks = number_of_stocks(amount_to_invest, price_list)
            portfolio = {k: v for k, v in zip(stb, numstocks)}
            

            
        elif risk_bearing_capability == "Moderate":
          price_list = []
          stb = []
          num = 0
          tick_list = []

          while num < 2:
               if mod_sorted.iloc[num]['Price'] < amount_to_invest:
                    price_list.append(mod_sorted.iloc[num]['Price'])
                    tick = mod_sorted.iloc[num]["Stock"]
                    stb.append(names.loc[names['tt'] == tick, 'stock'].values[0])
                    tick_list.append(tick)
                    num = num + 1

          num = 0
          while num < 1:
               if high_sorted.iloc[num]['Price'] < amount_to_invest:
                    price_list.append(high_sorted.iloc[num]['Price'])
                    tick = high_sorted.iloc[num]["Stock"]
                    stb.append(names.loc[names['tt'] == tick, 'stock'].values[0])
                    tick_list.append(tick)
                    num = num + 1

          num = 0
          while num < 1:
               if low_sorted.iloc[num]['Price'] < amount_to_invest:
                    price_list.append(low_sorted.iloc[num]['Price'])
                    tick = low_sorted.iloc[num]["Stock"]
                    stb.append(names.loc[names['tt'] == tick, 'stock'].values[0])
                    tick_list.append(tick)
                    num = num + 1

          numstocks = number_of_stocks(amount_to_invest, price_list)
          portfolio = {k: v for k, v in zip(stb, numstocks)}

            
        else:
            price_list = []
            tick_list = []
            stb = []
            num = 0
            while num < 3:
                if low_sorted.iloc[num]['Price'] < amount_to_invest:
                    price_list.append(low_sorted.iloc[num]['Price'])
                    tick = low_sorted.iloc[num]["Stock"]
                    stb.append(names.loc[names['tt'] == tick, 'stock'].values[0])
                    tick_list.append(tick)
                    num = num + 1
            
            numstocks = number_of_stocks(amount_to_invest, price_list)
            portfolio = {k: v for k, v in zip(stb, numstocks)}
            
     
        invested = 0
        for i in range(len(tick_list)):
            try:
                invested = invested+ (get_price(tick_list[i])*numstocks[i])
            except:
                invested = "Unable to Calculate at the moment"
        return render(request, 'stocks.html', {'amount_to_invest': amount_to_invest, 'risk_bearing_capability': risk_bearing_capability, 'portfolio': portfolio,  'current_value': 1, 'initial_value': invested})
    
    return render(request, "/Users/satyam/Desktop/Projects/ACM/acmsite/myapp/templates/stocks.html")

def new_view(request):
    current_value = np.random()
    return JsonResponse(request, 'stocks.html', {'current_value': current_value})
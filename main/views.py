from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import table_a
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from fbprophet import Prophet
import pandas as pd
import json,requests
from scipy.signal import find_peaks
from datetime import timedelta

def get_data(company_name='MSFT',interval='none'):
    apikey = 'B4R0YOLPQIDQ1OIL'
    print(interval)
    if interval == 'none':
        frequency = 'TIME_SERIES_DAILY'
        url = f"https://www.alphavantage.co/query?function={frequency}&symbol={company_name}&apikey={apikey}&outputsize=full"
        r = requests.get(url)
        data = r.json()
        df = pd.read_json(json.dumps(data['Time Series (Daily)'])).transpose().reset_index().rename(axis=1,mapper={'index':'ds'})
    else:
        frequency = 'TIME_SERIES_INTRADAY'
        url = f"https://www.alphavantage.co/query?function={frequency}&symbol={company_name}&apikey={apikey}&outputsize=full&interval={interval}"
        r = requests.get(url)
        data = r.json()
        df = pd.read_json(json.dumps(data[f"Time Series ({interval})"])).transpose().reset_index().rename(axis=1,mapper={'index':'ds'})
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.rename(axis=1,mapper={'1. open':'open',
                                  '5. volume':'volume',
                                 '2. high': 'high',
                                 '3. low': 'low',
                                 '4. close':'close'})
    return df


def homepage(request):
    return render(request,'main/homehome.html')

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created :{username}")
            login(request,user)
            messages.info(request,f"{username} successfully logged in")
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request,f"{msg}:{form.error_messages[msg]}")
                
    form = UserCreationForm
    return render(request,
                 "main/register.html",
                 context = {"form":form})


def logout_request(request):
    logout(request)
    messages.info(request,"logged out succesfully")
    return redirect("main:homepage")



def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request,data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not  None:
                login(request,user)
                messages.info(request,f"You are now logged in as {username} ")
                return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password")
        else:
            messages.error(request,"Invalid username or password")
            
    form = AuthenticationForm()
    return render(request,
                "main/login.html",
                {"form":form})


def select(request):
    if request.method == "POST":
        params = {}
        params['company_name'] = request.POST.get('company_name')
        company_name = params['company_name']
        number_of_forecasts = str(request.POST.get("number_of_forecasts"))
        type_ = request.POST.get('type')
        if company_name:
            df_daily = get_data(company_name=company_name,interval='none')
            df_hourly = get_data(company_name=company_name,interval='60min')
            df_daily = df_daily[['ds','close']]
            df_hourly = df_hourly[['ds','open']]

            request.session['data_daily'] = df_hourly.to_json()
            request.session['data_hourly'] = df_daily.to_json()
            request.session['company_name'] = company_name
            messages.info(request,f"the shape of the daily data is {df_daily.shape}")
            messages.info(request,f"the shape of the hourly data is {df_hourly.shape}")

            return redirect("main:homepage")
        else:
            messages.error(request,'The file could not be uploaded')
    else:
        pass
    return render(request,'main/select.html')

def visualise(request):

    data = request.session['data_daily']
    df = pd.read_json(data)
    df['ds'] = pd.to_datetime(df['ds'])
    df = df.sort_values(['ds'])
    return render(request,'main/visualise.html',
    {
        'y':df.open.values,
        'dates':df.ds.dt.date,


        }
                )




def fit_data(request):

    data = request.session['data']
    df = pd.read_json(data)
    df['ds'] = pd.to_datetime(df['ds'])
    
    n_forecasts = int(request.session['number_of_forecasts'])

    df = df.sort_values(['ds'])
    df_peaks = peak_detection(df)   
    params = request.session['params']
    M = Prophet()
    M.fit(df[['ds','y']])
    future = M.make_future_dataframe(periods=n_forecasts,freq = 'MS')
    forecast = M.predict(future)
    print(forecast['ds'])
    actuals = df['y'].values
    dates = df['ds'].dt.date.values
    preds = forecast['yhat'].iloc[-n_forecasts:].values
    preds_lower = forecast['yhat_lower'].iloc[-n_forecasts:].values
    preds_upper = forecast['yhat_upper'].iloc[-n_forecasts:].values
    pred_dates = forecast['ds'].dt.date.iloc[-n_forecasts:].values
    return render(request,'main/fit.html', 
            {
                'preds': preds ,
                'preds_lower':preds_lower,
                'preds_upper':preds_upper,
                'pred_dates': pred_dates,
                'actuals':actuals,
                'dates':dates,

            } 
                )            

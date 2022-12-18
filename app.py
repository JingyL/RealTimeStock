from flask import Flask, redirect, render_template, flash, session,request
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, StockOwning, Operation, User
from forms import UserForm, LoginForm, tradeForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy import asc
import requests
import json
import os
import re
import datetime
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
 
from twelvedata import TDClient
import websocket
import _thread
import time


api_key = "1dd61578f95549eaad51241b5b74a1fd"

uri = os.getenv("DATABASE_URL",'postgresql:///stock') 
if uri.startswith("postgres://"):
   uri = uri.replace("postgres://", "postgresql://", 1)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hellosecret')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

s_code = {"AL": "01", "AK": "54", "AZ": "02", "AR": "03", "CA": "04", 
        "CO": "05", "CT": "06", "DC": "08", "DE": "07", "FL": "09", "GA": "10", 
          "HI": "52", "ID": "11", "IL": "12", "IN": "13", "IA": "14", "KS": "15", 
          "KY": "16", "LA": "17", "ME": "18", "MD": "19",
          "MA": "20", "MI": "21", "MN": "22", "MS": "23", "MO": "24",
           "MT": "25", "NE": "26", "NV": "27", "NH": "28", "NJ": "29",
          "NM": "30", "NY": "36", "NC": "32", "ND": "33", "OH": "34", "OK": "35", 
          "OR": "36", "PA": "37", "RI": "38", "SC": "39",
          "SD": "40", "TN": "41", "TX": "42", "UT": "43", "VT": "44", "VA": "45", 
          "WA": "46", "WV": "47", "WI": "48", "WY": "49"}

##############################################################################
# register
# login
# logout
@app.route('/<username>')
def inital_page(username):
    if 'username' not in session or username != session['username']:
      # flash("Please login first!")
      return redirect('/login')
    buyingPower = User.query.filter_by(username=username).first().buying_power
    return render_template('base.html', buying_power=buyingPower)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form. first_name.data
        last_name = form.last_name.data
        city =  form.city.data
        state = form.state.data
        new_user = User.register(username, password, email, first_name, last_name, city, state)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        return redirect(f"/{session['username']}/stocks")

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['username'] = user.username
            session['user_id'] = user.id
            return redirect(f"/{session['username']}/stocks")
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    session.pop('user_id')
    # flash("Goodbye!", "info")
    return redirect('/login')
##############################################################################

# stock price page

@app.route('/<username>/stocks')
def show_stocks(username):
    user_id = session['user_id']
    symbols = ["AAPL", "MSFT", "TSLA", "AMZN", "GOOGL"]
    symbol_dict = {}
    # for symbol in symbols:
      # symbol_dict[symbol] = pull_data(symbol)
      # pull_data_image(symbol)
      # time.sleep(20)
    symbol_dict={
      "AAPL":100,
      "MSFT": 120,
      "TSLA": 130,
      "AMZN": 90,
      "GOOGL": 110
    }
    buyingPower = User.query.filter_by(username=username).first().buying_power
    print(buyingPower)
    shares = {}
    for symbol in symbols:
      res = StockOwning.query.filter_by(user_id=user_id, stock_symbol=symbol).first()
      print(symbol, res)
      if not res:
        shares[symbol] = 0
      else:
        shares[symbol] = res.quantity
      
    return render_template('stocks.html',symbol_dict=symbol_dict, buying_power=buyingPower, shares=shares)


def pull_data(Symbol):
    # Initialize client - apikey parameter is requiered
    td = TDClient(api_key)
 
    # Construct the necessary time series
    ts = td.time_series(
        symbol=Symbol,
        interval="1min",
        outputsize=1,
        timezone="America/New_York",
    )

    # fig = ts.with_ema(time_period=7).with_mama().with_mom().with_macd().as_plotly_figure()

    # fig.write_image("foo.png")
    
    tsp = ts.as_pandas()
 
    price = (tsp["high"].iloc[0] + tsp["low"].iloc[0]) / 2
    
    return price

def pull_data_image(Symbol):
    # Initialize client - apikey parameter is requiered
    td = TDClient(api_key)
 
    # Construct the necessary time series
    ts = td.time_series(
        symbol=Symbol,
        interval="1day",
        outputsize=75,
        timezone="America/New_York",
    )

    fig = ts.with_ema(time_period=7).with_mama().with_mom().with_macd().as_plotly_figure()

    fig.write_image(f'{Symbol}.png')
    
    tsp = ts.as_pandas()
 
    price = (tsp["high"].iloc[0] + tsp["low"].iloc[0]) / 2
    
    return price
    
##############################################################################
#  trade
@app.route('/<username>/trade', methods=['GET', 'POST'])
def user_trade(username):
    if 'username' not in session or username != session['username']:
        # flash("Please login first!")
        return redirect('/login')
    buyingPower = User.query.filter_by(username=username).first().buying_power
    form = tradeForm()
    if form.validate_on_submit():
        stock_name = form.stockname.data
        user_id = session['user_id']
        option = form.option.data
        shares = form.shares.data
        # db.session.add(new_board)
        # db.session.commit()
        # board = CollabBoard.query.filter_by(name=name).first()
        return redirect(f'/{username}/stocks', buying_power=buyingPower)

    return render_template('trade.html', form=form, buying_power=buyingPower)
    
 
@app.route('/<username>/trade/cal', methods=['GET', 'POST'])
def user_trade_cal(username):
    if 'username' not in session or username != session['username']:
        # flash("Please login first!")
        return redirect('/')
    form = tradeForm()
    if form.validate_on_submit():
        stockname = form.stockname.data
        user_id = session['user_id']
        option = form.option.data
        shares = form.shares.data
        user_buying_power = User.query.filter_by(username = username).first().buying_power
        current_price = pull_data(stockname)
      
        stockOwningQuery = StockOwning.query.filter_by(user_id = user_id, stock_symbol = stockname).first()
        if not stockOwningQuery:
          newStockowning = StockOwning(user_id = user_id, stock_symbol = stockname, quantity=0)
          db.session.add(newStockowning)
          db.session.commit()
          stockOwningQuery = StockOwning.query.filter_by(user_id = user_id, stock_symbol = stockname).first()
          
          

        if (option == "buy"):
          if user_buying_power < shares * current_price:
            #redirect to fail page
            flash('Buying power not enough')
            return redirect(f'/{username}/stocks')
          else: 
            user_buying_power -= shares * current_price
            stockOwningQuery.quantity += shares
        elif(option == "sell"):
          if(stockOwningQuery.quantity>shares):
            stockOwningQuery.quantity -= shares
            user_buying_power += shares * current_price
          else:
            flash('Shares Not Enough')
            return redirect(f'/{username}/stocks')


        user = User.query.filter_by(username = username).first()
        user.buying_power = user_buying_power
        db.session.commit()
    flash('Buy successfully')
    return redirect(f'/{username}/stocks')









#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
An algorithmic trading bot for Coinex Perpetual Futures.
Uses technical indicators from taapi.io to execute trades with risk management features.
"""

import json
import time
import datetime
import logging
import traceback
import schedule
import requests
from termcolor import colored
import api  # Custom API wrapper for Coinex

# ==============================================
# CONFIGURATION SECTION
# ==============================================

# Coinex API Credentials
ACCESS_ID = 'ACCESS_ID'
SECRET_KEY = 'SECRET_KEY'

# taapi.io API Key for technical indicators
INDICATOR_API_KEY = 'INDICATOR_API_KEY'

# ==============================================
# USER CONFIGURATION
# ==============================================

# Initialize bot with user preferences
answer = int(input("Initiate default settings? (1=Yes, 0=No) "))
market_indicator_api = input("Enter Market (e.g., ETH/USDT, BTC/USDT): ").upper()
market = market_indicator_api.replace("/", "")

"""
DEFAULT SETTINGS:
- Timeframe: 5m
- Indicators: 
  - MACD(14, 21, 15)
  - SAR(0.02, 0.2) 
  - ADX(24, 20.1)
- Leverage: 3
- Stoploss: 5% per trade
"""
if answer == 1:
    indicator_values = [14, 21, 15, 0.02, 0.2, 24, 20.1]
    leverage = 3
    timeframe = '5m'
    stoploss = 5
else:
    # Custom indicator parameters
    indicator_values = [
        input("MACD Fast Period: "),
        input("MACD Slow Period: "),
        input("MACD Signal Period: "),
        input("SAR Acceleration: "),
        input("SAR Maximum: "),
        input("ADX Period: "),
        float(input("ADX Level: "))
    ]
    leverage = int(input("Enter Leverage (3,5,8,10,15): "))
    stoploss = int(input("Enter stoploss for each trade (% based): "))
    timeframe = input("Enter Timeframe (5m,15m,30m,1h): ")

# Initialize Coinex API connection
robot = api.CoinexPerpetualApi(ACCESS_ID, SECRET_KEY)
robot.adjust_leverage(market, 1, leverage)

# Order amount truncation digits for different pairs
TRUNCATE_DIGITS = {
    "ETHUSDT": 3,
    "BTCUSDT": 4,
    "LTCUSDT": 1
}
truncate_digit = TRUNCATE_DIGITS.get(market, 2)  # Default to 2 if pair not specified

# ==============================================
# UTILITY FUNCTIONS
# ==============================================

def truncate(number: float, digits: int) -> float:
    """Truncate a number to specified decimal places without rounding."""
    pow10 = 10 ** digits
    return number * pow10 // 1 / pow10

def log_status(message: str, color: str = 'white'):
    """Log status messages with timestamp and colored output."""
    timestamp = datetime.datetime.now().replace(microsecond=0)
    print(colored(f"{message:10} {timestamp}", color), "\n", 70 * "-")

# ==============================================
# TRADING FUNCTIONS
# ==============================================

def risk_free():
    """Implement risk-free trading by setting stop orders after price moves favorably."""
    position_data = json.loads(json.dumps(robot.query_position_pending(market), indent=4))['data']
    
    if position_data != []:
        open_price = float(position_data[0]['open_price'])
        fresh_price = float(json.loads(json.dumps(robot.get_market_state(market), indent=4))['data']['ticker']['index_price'])
        side = int(position_data[0]['side'])
        amount = float(position_data[0]['amount'])

        # For long positions, set stop above entry after 1.1% profit
        if side == robot.ORDER_DIRECTION_BUY and fresh_price > open_price * 1.011:
            stop_price = open_price * 1.0015  # 0.15% above entry
            robot.put_stop_market_order(market, 1, amount, stop_price, 3)
        
        # For short positions, set stop below entry after 1.1% profit
        elif side == robot.ORDER_DIRECTION_SELL and fresh_price < open_price * 0.989:
            stop_price = open_price * 0.9985  # 0.15% below entry
            robot.put_stop_market_order(market, 2, amount, stop_price, 3)

def market_sell(market: str):
    """Execute market sell order with 3% of account balance and set stoploss."""
    deal_data = json.loads(json.dumps(robot.query_user_deals(market, 0, 1, 0), indent=4))
    position_type = deal_data['data']['records'][0]['side']
    stoploss_exist = int(json.loads(json.dumps(robot.query_stop_pending(market, 0, 0, 1)['data']['total'], indent=4)))
    
    if position_type == 2 or not stoploss_exist:
        robot.cancel_all_stop_order(market)
        
        # Close opposite position if exists
        position_id = json.loads(json.dumps(robot.query_user_deals(market, 0, 1, 2), indent=4)['data']['records'][0]['position_id'])
        robot.close_market(market, position_id)
        time.sleep(2)
        
        # Calculate order size (3% of available balance)
        available = float(json.loads(json.dumps(robot.query_account(), indent=4))['data']['USDT']['available'])
        index_price = float(json.loads(json.dumps(robot.get_market_state(market), indent=4))["data"]["ticker"]["index_price"])
        order_amount = truncate((available * 0.03) / index_price * leverage, truncate_digit)
        stop_price = index_price * (1 + stoploss / 100)
      
        # Place sell order and stoploss
        robot.put_market_order(market, robot.ORDER_DIRECTION_SELL, order_amount)
        robot.put_stop_market_order(market, 2, order_amount, stop_price, 3)

def market_buy(market: str):
    """Execute market buy order with 3% of account balance and set stoploss."""
    deal_data = json.loads(json.dumps(robot.query_user_deals(market, 0, 1, 0), indent=4))
    position_type = deal_data['data']['records'][0]['side']
    stoploss_exist = int(json.loads(json.dumps(robot.query_stop_pending(market, 0, 0, 1)['data']['total'], indent=4)))
    
    if position_type == 1 or not stoploss_exist:
        robot.cancel_all_stop_order(market)
        
        # Close opposite position if exists
        position_id = json.loads(json.dumps(robot.query_user_deals(market, 0, 1, 1), indent=4)['data']['records'][0]['position_id'])
        robot.close_market(market, position_id)
        time.sleep(2)
        
        # Calculate order size (3% of available balance)
        available = float(json.loads(json.dumps(robot.query_account(), indent=4))['data']['USDT']['available'])
        index_price = float(json.loads(json.dumps(robot.get_market_state(market), indent=4))["data"]["ticker"]["index_price"])
        order_amount = truncate((available * 0.03) / index_price * leverage, truncate_digit)
        stop_price = index_price * (1 - stoploss / 100)

        # Place buy order and stoploss
        robot.put_market_order(market, robot.ORDER_DIRECTION_BUY, order_amount)
        robot.put_stop_market_order(market, 1, order_amount, stop_price, 3)

# ==============================================
# TECHNICAL INDICATOR FUNCTIONS
# ==============================================

def get_indicator_data(indicator: str, params: dict) -> dict:
    """Fetch indicator data from taapi.io API with error handling."""
    endpoint = f"https://api.taapi.io/{indicator}"
    params['secret'] = INDICATOR_API_KEY
    params['exchange'] = 'binance'
    params['symbol'] = market_indicator_api
    params['interval'] = timeframe
    
    try:
        time.sleep(5)  # Rate limiting
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {indicator} data: {str(e)}")
        return None

def macd() -> int:
    """Get trading signal from MACD indicator."""
    params = {
        'backtracks': '3',
        'optInFastPeriod': indicator_values[0],
        'optInSlowPeriod': indicator_values[1],
        'optInSignalPeriod': indicator_values[2]
    }
    time.sleep(15.5)
    data = get_indicator_data("macd", params)
    if not data:
        return 0
        
    hist_current = float(data[1]['valueMACDHist'])
    hist_previous = float(data[2]['valueMACDHist'])
    
    print(f"MACD: {hist_current:.4f} (Prev: {hist_previous:.4f})\n")
    
    # Buy signal when histogram crosses above zero
    if hist_current > 0 > hist_previous:
        return robot.ORDER_DIRECTION_BUY
    # Sell signal when histogram crosses below zero
    elif hist_current < 0 < hist_previous:
        return robot.ORDER_DIRECTION_SELL
    return 0

def sar() -> int:
    """Get trading signal from Parabolic SAR indicator."""
    params_1 = {
        'backtracks': '4',
        'optInAcceleration': indicator_values[3],
        'optInMaximum': indicator_values[4]
    }
    params_2 = {
        'backtracks': '4'
    }
    time.sleep(15.5)
    data_1 = get_indicator_data("sar", params_1)
    if not data:
        return 0
    time.sleep(15.5)
    data_2 = get_indicator_data("candle", params_2)
    sar = float(json.loads(json.dumps(data_1.json(), indent=4))[1]['value'])
    price = float(json.loads(json.dumps(params_2.json(), indent=4))[1]['close'])

    print("SAR:", price, sar, "\n")
    # Sell signal when SAR value is above price
    if price < sar:
        return robot.ORDER_DIRECTION_SELL
    # Buy signal when SAR value is below price
    elif price > sar:
        return robot.ORDER_DIRECTION_BUY
    return 0

def adx() -> int:
    """Get trading permission signal from ADX indicator."""
    params = {
        'backtracks': '3',
        'optInTimePeriod': indicator_values[5]
    }
    time.sleep(15.5)
    data = get_indicator_data("adx", params)
    adx_value = float(json.loads(json.dumps(data.json(), indent=4))[1]['value'])

    print("ADX:", adx_value, "\n")
    # Permit trade if the trend is strong enough.
    if adx_value > indicator_values[6]:
        return 1
    # Block trade if the trend is weak enough/market is in range.
    else:
        return 0
# Extra ready to use indicators:
def supertrend() -> int:
    """Get trading signal from Supertrend indicator."""
    params = {
        'backtracks': '3',
        'period': 15,
        'multiplier': 10
    }
    
    data = get_indicator_data("supertrend", params)
    if not data:
        return 0
        
    current_signal = data[1]['valueAdvice']
    previous_signal = data[2]['valueAdvice']
    
    print(f"SUPERTREND: Current={current_signal}, Previous={previous_signal}\n")
    
    # Buy signal when trend changes from short to long
    if current_signal == "long" and previous_signal == "short":
        return 1
    return 0

def rsi() -> int:
    """Get trading signal from RSI indicator."""
    params = {
        'backtracks': '3',
        'optInTimePeriod': indicator_values[5]
    }
    
    data = get_indicator_data("rsi", params)
    if not data:
        return 0
        
    rsi_value = float(data[1]['value'])
    print(f"RSI: {rsi_value:.2f}\n")
    
    # Signal when RSI is between 30-70 (not overbought/sold)
    return 1 if 30 < rsi_value < 70 else 0

# ==============================================
# TRADING STRATEGY
# ==============================================

def signal_helper():
    """Main trading strategy that combines indicators to generate signals."""
    try:
        risk_free()  # Manage risk for open positions
        
        # Get signals from indicators
        macd_signal = macd()
        sar_signal = sar()
        adx_signal = adx()
        
        # Execute trades based on combined signals
        if macd_signal == robot.ORDER_DIRECTION_BUY and sar_signal == robot.ORDER_DIRECTION_BUY and adx_signal:
            market_buy(market)
            log_status("BUY", 'green')
        elif macd_signal == robot.ORDER_DIRECTION_SELL and sar_signal == robot.ORDER_DIRECTION_SELL and adx_signal:
            market_sell(market)
            log_status("SELL", 'red')
        else:
            log_status("NO SIGNAL", 'yellow')
            
    except Exception as e:
        logging.error(traceback.format_exc())
        log_status("ERROR", 'red')

# ==============================================
# SCHEDULER SETUP
# ==============================================

# Configure schedule based on selected timeframe
SCHEDULE_CONFIG = {
    '5m': [
        ':00', ':05', ':10', ':15', ':20', ':25', 
        ':30', ':35', ':40', ':45', ':50', ':55'
    ],
    '15m': [':01', ':16', ':31', ':46'],
    '30m': [':01', ':31'],
    '1h': [':01']
}

for minute in SCHEDULE_CONFIG.get(timeframe, []):
    schedule.every().hour.at(minute).do(signal_helper)

# ==============================================
# MAIN EXECUTION LOOP
# ==============================================

log_status("OPERATIONAL", 'green')

while True:
    schedule.run_pending()
    time.sleep(1)

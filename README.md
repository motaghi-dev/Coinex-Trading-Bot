
# 📈 Coinex Perpetual Futures Trading Bot


![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)


An algorithmic trading bot for [**Coinex cryptocurrency perpetual futures**](https://www.coinex.com) markets, integrating [**taapi.io**](https://taapi.io/) technical indicators for automated trading strategies and dynamic risk management.

---

## Overview

This project is a Python-based trading bot built for the [**Coinex Perpetual Futures**](https://www.coinex.com) market. It uses [**Coinex API**](https://coinexcom.github.io/coinex_api_en_doc/futures/) for market data and order execution, and [**taapi.io API**](https://taapi.io/documentation/) for fetching a variety of technical indicators in real-time. The bot is capable of:
- Executing market and stop orders.
- Managing open positions dynamically.
- Applying risk management strategies.
- Supporting adjustable leverage levels.
- Running continuous, interval-based signal scanning.
- Supporting customizable technical indicator-based strategies.

---

## Execution Flow

```
+-------------------------+
|   Fetch Market Data     |
+-------------------------+
             |
             v
+-------------------------+
| Retrieve Indicator Data |
|  (MACD, SAR, ADX, etc.) |
+-------------------------+
            |
            v
+-------------------------+
| Generate Trading Signal |
+-------------------------+
            |
      +-----+-----+
      |           |
      v           v
  Open Trade   No Action
      |           
      v
+-------------------------+
|  Stop-Loss / RiskFree   |
+-------------------------+
            |
            v
+-------------------------+
|   Monitor and Adjust    |
+-------------------------+
```



---

##  Project Structure

```
.
├── Main.py               # Core trading bot logic
├── api.py                # Coinex API wrapper (provided by Coinex)
├── request_client.py     # HTTP client with signing and authorization (provided by Coinex)
└── README.md             # Project description and documentation
```

---

##  Features

✅ Coinex perpetual market integration  
✅ Adjustable leverage options: `3x`, `5x`, `8x`, `10x`, `15x`  
✅ Uses multiple **technical indicators** via [**taapi.io**](https://taapi.io/)  
✅ Dynamic stop-loss and risk-free management  
✅ Market-neutral exit strategies on signal reversal  
✅ Designed for **continuous operation** using Python's `schedule` module  
✅ Easily extendable to new strategies and risk models  

---

##  Default Strategy

The bot's default strategy is a trend following implementation at its core and utilizes widely used technical indicators, computed via taapi.io API, and executed against live Coinex orderbooks.

###  Indicator Logic Example:

```python
# MACD Signal Extraction
params = {
    'backtracks': '3',
    'optInFastPeriod': 14,
    'optInSlowPeriod': 21,
    'optInSignalPeriod': 15
}
data = get_indicator_data("macd", params)
hist_current = float(data[1]['valueMACDHist'])
hist_previous = float(data[2]['valueMACDHist'])

if hist_current > 0 > hist_previous:
    return robot.ORDER_DIRECTION_BUY
elif hist_current < 0 < hist_previous:
    return robot.ORDER_DIRECTION_SELL
return 0
```

This process is repeated for each indicator (SAR, ADX, etc.) and their combined result triggers trade execution decisions.

### **Indicators used by the bots default strategy:**


- [**MACD**](https://taapi.io/indicators/macd/) (`14, 21, 15`):
  -  ##### A trend-following **momentum** indicator
- [**SAR (Parabolic SAR)**](https://taapi.io/indicators/parabolic-sar/) (`0.02, 0.2`)
  -  ##### A trend reversal indicator
- [**ADX**](https://taapi.io/indicators/adx/) (`24, 20.1`)
  -  ##### A trend strength indicator

#### The strategy relys on clear short/medium term price swings in either direction. It's trend following in nature and produces well-balanced returns in trending markets.
Here are what valid long and short signals might look like:

![Buy signal](https://github.com/motaghi-dev/Coinex-Trading-Bot/blob/main/src/BuySignal.png)


---

## 🛡️ Risk Management

Cryptocurrency markets are inherently volatile and unpredictable. To address this, the bot implements:

- **Fixed Percentage Stop-Losses**: Every trade automatically sets a stop-loss at a pre-defined percentage level.
- **Risk-Free Trade Management**: If a trade moves in favor, the stop-loss is adjusted to the entry price to secure profits and prevent loss.
- **Position Sizing**: Each trade uses only **3% of the account's available balance** to manage exposure.
- **Dynamic leverage management** as per user-defined configurations.

---

## 🔧 Configuration & Customization

The bot can be configured interactively at runtime or use default preset values.

**Default Parameters:**

| Parameter      | Value        |
|:---------------|:--------------|
| Timeframe       | `5m`          |
| Leverage        | `3x`          |
| Stop-Loss       | `5%` per trade |
| [MACD](https://taapi.io/indicators/macd/)            | `(14, 21, 15)` |
| [SAR](https://taapi.io/indicators/parabolic-sar/)             | `(0.02, 0.2)` |
| [ADX](https://taapi.io/indicators/adx/)             | `(24, 20.1)` |

**Custom Configuration:**

At startup, the bot prompts the user to either use default settings or input custom values for:

- Market pair (e.g., `BTC/USDT`)
- Leverage
- Timeframe
- Indicator parameters
- Stop-loss percentage  

---

## 🛠️ Setup & Installation

1. **Clone this repository**

```bash
git clone https://github.com/yourusername/coinex-trading-bot.git
cd coinex-trading-bot
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

_Example dependencies (include these in your `requirements.txt` file):_

```
requests
schedule
termcolor
```

3. **Set your API Credentials**

In `Main.py`:

```python
ACCESS_ID = 'YOUR_COINEX_ACCESS_ID'
SECRET_KEY = 'YOUR_COINEX_SECRET_KEY'
INDICATOR_API_KEY = 'YOUR_TAAPI_API_KEY'
```

---

## 🚀 Running the Bot

Simply run:

```bash
python Main.py
```

The bot will prompt for configuration and then start trading based on the defined strategy and risk management rules.

---

## 📈 Future Development

Planned enhancements:

- Portfolio-level risk management tools
- Expanded strategy framework (including correlation-based, sentiment, and intermarket analysis)
- Trade history logging and performance reporting
- Telegram/Discord notifications
- Docker deployment support
- Multi-exchange support via modular API wrappers

---

## 📜 Disclaimer

> **⚠️ Warning:**  
> Trading cryptocurrencies involves a **high level of risk**. This bot is designed for educational and personal use purposes. You are solely responsible for your trades and financial decisions. Use this software at your own risk.

---

## 📬 Contact

If you have questions, ideas, or would like to collaborate:

- 📧 Email: your_email@example.com
- 📱 Telegram: [@yourhandle](https://t.me/yourhandle)

---

## ⭐️ Show your support

If you find this project helpful, feel free to star the repository ⭐️ and share it!

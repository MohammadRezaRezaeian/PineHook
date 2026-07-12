# PineHook: TradingView to MetaTrader 5 Bridge

PineHook is a high-performance, modular Python application built with **FastAPI** that acts as a bridge between **TradingView Webhooks** and **MetaTrader 5 (MT5)**. It allows you to execute fully automated trading strategies sent from Pine Script directly into one or multiple MT5 accounts simultaneously.

---

## ⚙️ How It Works

TradingView cannot send trades directly to MT5. PineHook serves as the middleman:
1. **The Signal:** A Pine Script strategy triggers an alert on TradingView.
2. **The Webhook:** TradingView sends an HTTP POST request containing a formatted JSON payload to the PineHook server.
3. **The Router:** FastAPI receives the payload and validates the security passphrase.
4. **The Logic:** The Trade Service identifies the strategy and finds the subscribed MT5 accounts.
5. **The Execution:** The MT5 Engine connects to the specific MetaTrader 5 terminal path for each user and executes the MQL5 `OrderSend` request instantly.

---

## ⚠️ Important Prerequisites

* **Windows OS / Windows VPS:** The `MetaTrader5` Python library **only** runs on Windows because it must interact directly with the desktop MT5 terminal executable.
* **Python 3.9+** installed on your machine.
* **MetaTrader 5** installed and logged into your broker account.
* **Algo Trading Enabled:** In your MT5 terminal, ensure the "Algo Trading" button at the top is green.
* **TradingView Paid Plan:** TradingView requires at least the "Essential" tier to use Webhook URLs.

---

## 📊 Phase 1: TradingView Setup

To trigger trades, your Pine Script must construct a JSON payload and send it to your server.

### 1. The Pine Script & JSON Payload
Add this logic to your TradingView Pine Script to fire the Universal MQL5 JSON payload:

```pine
//@version=5
indicator("PineHook Webhook Signal", overlay=true)

// Signal Logic Example
buySignal = ta.crossover(ta.ema(close, 9), ta.ema(close, 21))

// JSON Template
var string jsonTemplate = '{"passphrase": "{0}", "strategy_id": "{1}", "action": "{2}", "symbol": "{3}", "type": "{4}", "volume": {5}, "price": {6}, "sl": {7}, "tp": {8}, "deviation": {9}, "magic_number": {10}, "comment": "{11}"}'

if buySignal
    string alertJson = str.format(jsonTemplate, 
      "MySecretToken123", // passphrase
      "EMA_Crossover",    // strategy_id
      "deal",             // action
      syminfo.ticker,     // symbol
      "buy",              // type
      0.1,                // volume (lots)
      close,              // price
      0.0,                // sl
      0.0,                // tp
      10,                 // deviation
      777888,             // magic_number
      "TV_Buy_Signal"     // comment
      )
    alert(alertJson, alert.freq_once_per_bar_close)
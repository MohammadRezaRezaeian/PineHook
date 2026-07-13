# PineHook: TradingView to MetaTrader 5 Bridge

PineHook is a high-performance, modular Python application built with **FastAPI** that acts as a secure bridge between **TradingView Webhooks** and **MetaTrader 5 (MT5)**. It allows you to execute fully automated trading strategies sent from Pine Script directly into one or multiple MT5 accounts simultaneously.

## ✨ Features
* **Market Execution:** Instant Buy/Sell market orders.
* **Pending Orders:** Support for Buy Limit, Sell Limit, Buy Stop, and Sell Stop.
* **Trade Management:** Automatically close open positions or cancel pending orders directly from TradingView signals.
* **Multi-Account Support:** Route different strategies to different MT5 terminals.
* **Secure:** Passphrase protection ensures only your TradingView alerts can trigger trades.

---

## ⚠️ Important Prerequisites

* **Windows OS / Windows VPS:** The `MetaTrader5` Python library **only** runs on Windows because it must interact directly with the desktop MT5 terminal executable.
* **Python 3.9+** installed on your machine.
* **MetaTrader 5** installed and logged into your broker account.
* **Algo Trading Enabled:** In your MT5 terminal, ensure the "Algo Trading" button at the top is green.
* **TradingView Paid Plan:** TradingView requires at least the "Essential" tier to use Webhook URLs.

---

## 🌐 The Webhook URL: How TradingView Connects to PineHook

**Crucial Concept:** You *do not* write the API URL inside your Pine Script code. Pine Script does not have an `http.post()` function. Instead, your Pine Script generates a JSON message, and you paste your server's URL into the TradingView UI.

When you run this project, FastAPI creates a specific endpoint that listens for TradingView signals. 

### The Exact URL You Will Use
Your API endpoint is always:
`/api/v1/tv-webhook`

* **If running locally with Ngrok:** `https://<your-ngrok-id>.ngrok-free.app/api/v1/tv-webhook`
* **If hosted on a VPS/Server:** `http://<your-server-ip>:8000/api/v1/tv-webhook`
* **If using a custom domain:** `https://api.yourdomain.com/api/v1/tv-webhook`

You will paste this exact URL into the **Webhook URL** box in TradingView's Alert creation menu (detailed in Phase 1).

---

## 📊 Phase 1: TradingView Setup (Pine Script & Alerts)

To trigger trades, your Pine Script must construct a JSON payload and fire it using the `alert()` function. 

### 1. The Pine Script Template
Add this logic to your TradingView Pine Script. Notice how we use a single JSON template but change the `action` and `type` fields based on what we want to do.

```pine
//@version=5
indicator("PineHook Advanced Signals", overlay=true)

var string WEBHOOK_TOKEN = "MySecretToken123"
var string STRAT_ID = "EMA_Crossover"
var int MAGIC = 777888

// --- The JSON Template ---
var string jsonTemplate = '{"passphrase": "{0}", "strategy_id": "{1}", "action": "{2}", "symbol": "{3}", "type": "{4}", "volume": {5}, "price": {6}, "sl": {7}, "tp": {8}, "deviation": {9}, "magic_number": {10}, "comment": "{11}"}'

// ---------------------------------------------------------
// SCENARIO A: Market Execution (Buy/Sell)
// ---------------------------------------------------------
if ta.crossover(close, ta.sma(close, 50))
    // action: "deal", type: "buy" or "sell"
    string buyJson = str.format(jsonTemplate, WEBHOOK_TOKEN, STRAT_ID, "deal", syminfo.ticker, "buy", 0.1, close, 0.0, 0.0, 10, MAGIC, "Market Buy")
    alert(buyJson, alert.freq_once_per_bar_close)

// ---------------------------------------------------------
// SCENARIO B: Place a Pending Order (Limit/Stop)
// ---------------------------------------------------------
if ta.crossunder(close, ta.sma(close, 50))
    // action: "pending", type: "buy_limit", "sell_limit", "buy_stop", "sell_stop"
    float limitPrice = close - (20 * syminfo.mintick * 10)
    string pendingJson = str.format(jsonTemplate, WEBHOOK_TOKEN, STRAT_ID, "pending", syminfo.ticker, "buy_limit", 0.1, limitPrice, 0.0, 0.0, 10, MAGIC, "Limit Entry")
    alert(pendingJson, alert.freq_once_per_bar_close)

// ---------------------------------------------------------
// SCENARIO C: Close Open Positions
// ---------------------------------------------------------
bool exitSignal = ta.crossunder(ta.ema(close, 9), ta.ema(close, 21))
if exitSignal
    // action: "close". MT5 will find positions matching the symbol and magic number.
    string closeJson = str.format(jsonTemplate, WEBHOOK_TOKEN, STRAT_ID, "close", syminfo.ticker, "all", 0.0, 0.0, 0.0, 0.0, 10, MAGIC, "Exit Signal")
    alert(closeJson, alert.freq_once_per_bar_close)

// ---------------------------------------------------------
// SCENARIO D: Cancel Pending Orders
// ---------------------------------------------------------
bool setupInvalidated = close < ta.sma(close, 200)
if setupInvalidated
    // action: "cancel". MT5 will remove unfilled orders matching the symbol and magic number.
    string cancelJson = str.format(jsonTemplate, WEBHOOK_TOKEN, STRAT_ID, "cancel", syminfo.ticker, "all", 0.0, 0.0, 0.0, 0.0, 10, MAGIC, "Cancel Pending")
    alert(cancelJson, alert.freq_once_per_bar_close)
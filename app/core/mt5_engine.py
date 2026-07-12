import MetaTrader5 as mt5

class MT5Engine:
    @staticmethod
    def execute_trade(user_config: dict, signal: dict) -> dict:
        # 1. Initialize specific terminal instance for this user
        initialized = mt5.initialize(
            path=user_config["mt5_path"],
            login=user_config["mt5_login"],
            password=user_config["mt5_password"],
            server=user_config["mt5_server"]
        )
        
        if not initialized:
            return {"status": "error", "message": f"Failed to connect to MT5 for user {user_config['user_id']}"}

        # 2. Map actions (simplified for brevity)
        action_map = {"deal": mt5.TRADE_ACTION_DEAL}
        type_map = {"buy": mt5.ORDER_TYPE_BUY, "sell": mt5.ORDER_TYPE_SELL}

        request_dict = {
            "action": action_map.get(signal.action.lower(), mt5.TRADE_ACTION_DEAL),
            "symbol": signal.symbol,
            "volume": signal.volume,
            "type": type_map.get(signal.type.lower()),
            "price": signal.price,
            "sl": signal.sl,
            "tp": signal.tp,
            "deviation": signal.deviation,
            "magic": signal.magic_number,
            "comment": signal.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # 3. Send Order
        result = mt5.order_send(request_dict)
        
        # We don't shut down MT5 here; we just disconnect the Python binding
        # so it's free to bind to the next terminal in the loop.
        mt5.shutdown()

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            return {"status": "error", "message": "Order failed"}

        return {"status": "success", "order": result.order}
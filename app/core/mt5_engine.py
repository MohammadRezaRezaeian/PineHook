import MetaTrader5 as mt5

class MT5Engine:
    @staticmethod
    def execute_trade(user_config: dict, signal) -> dict:
        initialized = mt5.initialize(
            path=user_config["mt5_path"],
            login=user_config["mt5_login"],
            password=user_config["mt5_password"],
            server=user_config["mt5_server"]
        )
        
        if not initialized:
            return {"status": "error", "message": f"Failed to connect to MT5 for user {user_config['user_id']}"}

        symbol = signal.symbol
        magic = signal.magic_number
        action = signal.action.lower()

        # ---------------------------------------------------------
        # ACTION: CLOSE POSITION(S)
        # ---------------------------------------------------------
        if action == "close":
            positions = mt5.positions_get(symbol=symbol)
            if positions is None or len(positions) == 0:
                mt5.shutdown()
                return {"status": "ignored", "message": "No open positions found to close."}

            results = []
            for pos in positions:
                if pos.magic == magic:
                    # To close, we send a deal in the OPPOSITE direction
                    close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
                    tick = mt5.symbol_info_tick(symbol)
                    price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask

                    request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": symbol,
                        "volume": pos.volume,
                        "type": close_type,
                        "position": pos.ticket, # Crucial: tells MT5 which position to close
                        "price": price,
                        "deviation": signal.deviation,
                        "magic": magic,
                        "comment": signal.comment,
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    res = mt5.order_send(request)
                    results.append(res.retcode == mt5.TRADE_RETCODE_DONE)

            mt5.shutdown()
            return {"status": "success", "message": f"Closed {len(results)} positions."}

        # ---------------------------------------------------------
        # ACTION: CANCEL PENDING ORDER(S)
        # ---------------------------------------------------------
        if action == "cancel":
            orders = mt5.orders_get(symbol=symbol)
            if orders is None or len(orders) == 0:
                mt5.shutdown()
                return {"status": "ignored", "message": "No pending orders found to cancel."}

            results = []
            for order in orders:
                if order.magic == magic:
                    # TRADE_ACTION_REMOVE requires only the action and the order ticket
                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order.ticket
                    }
                    res = mt5.order_send(request)
                    results.append(res.retcode == mt5.TRADE_RETCODE_DONE)

            mt5.shutdown()
            return {"status": "success", "message": f"Cancelled {len(results)} pending orders."}

        # ---------------------------------------------------------
        # ACTION: MARKET DEAL OR PENDING ORDER
        # ---------------------------------------------------------
        # Map incoming types to exact MT5 constants
        type_map = {
            "buy": mt5.ORDER_TYPE_BUY,
            "sell": mt5.ORDER_TYPE_SELL,
            "buy_limit": mt5.ORDER_TYPE_BUY_LIMIT,
            "sell_limit": mt5.ORDER_TYPE_SELL_LIMIT,
            "buy_stop": mt5.ORDER_TYPE_BUY_STOP,
            "sell_stop": mt5.ORDER_TYPE_SELL_STOP
        }

        mt5_action = mt5.TRADE_ACTION_PENDING if action == "pending" else mt5.TRADE_ACTION_DEAL
        mt5_type = type_map.get(signal.type.lower())

        if mt5_type is None:
            mt5.shutdown()
            return {"status": "error", "message": f"Unsupported order type: {signal.type}"}

        # Determine execution price if it's a market deal
        execution_price = signal.price
        if mt5_action == mt5.TRADE_ACTION_DEAL:
            tick = mt5.symbol_info_tick(symbol)
            execution_price = tick.ask if mt5_type == mt5.ORDER_TYPE_BUY else tick.bid

        request_dict = {
            "action": mt5_action,
            "symbol": symbol,
            "volume": signal.volume,
            "type": mt5_type,
            "price": execution_price,
            "sl": signal.sl,
            "tp": signal.tp,
            "deviation": signal.deviation,
            "magic": magic,
            "comment": signal.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request_dict)
        mt5.shutdown()

        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            error_code = result.retcode if result else "Unknown"
            return {"status": "error", "message": f"Order failed. MT5 Retcode: {error_code}"}

        return {"status": "success", "order_id": result.order}
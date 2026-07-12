import json
import os
from app.core.mt5_engine import MT5Engine

class TradeService:
    def __init__(self):
        # Load our mock database of users
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
        with open(db_path, 'r') as f:
            self.users = json.load(f)

    def process_signal(self, signal) -> dict:
        results = {}
        
        # Find all users subscribed to the strategy that fired
        target_users = [
            u for u in self.users 
            if signal.strategy_id in u.get("subscribed_strategies", [])
        ]

        if not target_users:
            return {"status": "ignored", "message": "No users subscribed to this strategy"}

        # Execute trade for each target user sequentially
        for user in target_users:
            # Here we pass the signal to the MT5 Engine for this specific user
            execution_result = MT5Engine.execute_trade(user_config=user, signal=signal)
            results[user["user_id"]] = execution_result

        return {
            "status": "processed",
            "strategy": signal.strategy_id,
            "executions": results
        }
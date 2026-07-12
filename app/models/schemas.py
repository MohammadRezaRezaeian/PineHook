from pydantic import BaseModel

class WebhookPayload(BaseModel):
    passphrase: str
    strategy_id: str     
    action: str          
    symbol: str
    type: str            
    volume: float        
    price: float
    sl: float = 0.0
    tp: float = 0.0
    deviation: int = 10
    magic_number: int = 777888
    comment: str = "PineHook Signal"
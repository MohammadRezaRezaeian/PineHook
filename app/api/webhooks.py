from fastapi import APIRouter, HTTPException, status
from app.models.schemas import WebhookPayload
from app.services.trade_service import TradeService

router = APIRouter()
trade_service = TradeService()

WEBHOOK_PASSPHRASE = "MySecretToken123"

@router.post("/tv-webhook")
async def handle_tradingview_alert(payload: WebhookPayload):
    # Security check
    if payload.passphrase != WEBHOOK_PASSPHRASE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Passphrase")
    
    # Hand off to the business logic layer
    result = trade_service.process_signal(payload)
    
    return result
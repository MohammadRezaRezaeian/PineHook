from fastapi import FastAPI
from app.api.webhooks import router as webhook_router

app = FastAPI(title="PineHook Multi-User Engine")

# Include our webhook routes
app.include_router(webhook_router, prefix="/api/v1")
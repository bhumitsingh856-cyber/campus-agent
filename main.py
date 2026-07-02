from fastapi import FastAPI
from src.routes.telegram import telegram_router, telegram_app
from src.routes.bot import bot_router
from src.routes.whatsapp import whatsapp_router
import os

app = FastAPI()

app.include_router(telegram_router)
app.include_router(bot_router)
app.include_router(whatsapp_router)


@app.get("/")
def helth():
    return {"success": True}


@app.on_event("startup")
async def setup_webhook():
    """Set Telegram webhook on startup"""
    webhook_url = f"{os.getenv('TELEGRAM_WEBHOOK_URL' )}"
    await telegram_app.bot.set_webhook(webhook_url)

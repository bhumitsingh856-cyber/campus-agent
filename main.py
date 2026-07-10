from fastapi import FastAPI
from src.routes.telegram import telegram_router, telegram_app
from src.routes.bot import bot_router
from src.routes.whatsapp import whatsapp_router
from src.routes.admin import admin_router
import os
from contextlib import asynccontextmanager
from src.db.checkpointer import init_db, close_db
import src.agent.workflow as workflow
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhook_url = f"{os.getenv('TELEGRAM_WEBHOOK_URL') }"
    await telegram_app.bot.set_webhook(webhook_url)
    await init_db()
    workflow.get_workflow()
    print("Database initialized successfully.")
    yield
    await close_db()
    print("Database closed successfully.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(telegram_router)
app.include_router(bot_router)
app.include_router(whatsapp_router)
app.include_router(admin_router)


@app.get("/")
def helth():
    return {"success": True}



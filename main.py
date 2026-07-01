from fastapi import FastAPI, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from src.agent.workflow import wf
from src.agent.workflow import checkpoint
from langchain_core.messages import HumanMessage
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from telegram.constants import ParseMode

import html
import os

TOKEN = os.getenv("TELEGRAM_ACCESS_TOKEN")
telegram_app = Application.builder().token(TOKEN).build()

app = FastAPI()


@app.get("/")
def helth():
    return {"success": True}


@app.on_event("startup")
async def setup_webhook():
    """Set Telegram webhook on startup"""
    webhook_url = "https://daunting-pushover-unbolted.ngrok-free.dev/telegram"
    await telegram_app.bot.set_webhook(webhook_url)


@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Receive messages from Telegram"""
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    user_query :str= update.message.text
    user_id = update.effective_user.id

    if(user_query.lower().strip() =="/clear"):
        try:
            checkpoint.storage.pop(user_id)
            await telegram_app.bot.send_message(
                chat_id=user_id,
                text="Conversation memory cleared successfully ✔️",
                parse_mode=ParseMode.MARKDOWN,
            )
            return {"status": "ok", "message": "cleared"}
        except Exception as e:
            print(e)
            await telegram_app.bot.send_message(
                chat_id=user_id,
                text="Unable to delete Conversation memory, please try agin ❌ ",
                parse_mode=ParseMode.MARKDOWN,
            )
            return {"status": "error", "message": "failed"}

    print("User- ", user_query)
    try:
        result = await wf.ainvoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"configurable": {"thread_id": 11}},
        )

        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=result["messages"][-1].content,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text="Something went, please try again later !",
            parse_mode=ParseMode.MARKDOWN,
        )
    return {"status": "ok"}


@app.post("/bot")
async def bot(req: str):
    res = await wf.ainvoke(
        {"messages": [HumanMessage(content=req)]},
        config={"configurable": {"thread_id": 0.11}},
    )
    return {res["messages"][-1].content}


@app.post("/whatsapp-webhook")
async def whatsapp_webhook(req: Request):
    form = await req.form()
    threadId = form.get("WaId")
    body = form.get("Body")
    res = MessagingResponse()
    try:
        agent_res = await wf.ainvoke(
            {"messages": [HumanMessage(content=body)]},
            config={"configurable": {"thread_id": threadId}},
        )
        res.message(agent_res["messages"][-1].content)
        return Response(content=str(res), media_type="application/xml")
    except Exception as e:
        res.message("Something went, please try again later !")
        return Response(content=str(res), media_type="application/xml")

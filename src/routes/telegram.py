from fastapi import Request, APIRouter
from telegram import Update
from telegram.ext import Application
from telegram.constants import ParseMode
from telegram.constants import ChatAction
from langchain_core.messages import HumanMessage
from src.agent.workflow import wf
from src.utils.command_handler import process_command
from src.utils.start_message import start_message
import os

TOKEN = os.getenv("TELEGRAM_ACCESS_TOKEN")
telegram_app = Application.builder().token(TOKEN).build()

telegram_router = APIRouter()


@telegram_router.post("/telegram")
async def telegram_webhook(request: Request):
    """Receive messages from Telegram"""
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)

    if update.message is None or update.message.text is None:
        return {"status": "ok"}
    user_query: str = update.message.text
    user_id = update.effective_user.id

    command_result = process_command(user_query, user_id)
    if command_result["handled"]:
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=command_result["message"],
            parse_mode=ParseMode.MARKDOWN,
        )
        return {"status": "ok"}

    try:
        
        await telegram_app.bot.send_chat_action(
            chat_id=user_id, action=ChatAction.TYPING
        )
        result = await wf.ainvoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"configurable": {"thread_id": user_id}},
        )

        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=result["messages"][-1].content,
            # text="LLM",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        print(e)
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text="*Something went, please try again later !*",
            parse_mode=ParseMode.MARKDOWN,
        )
    return {"status": "ok"}

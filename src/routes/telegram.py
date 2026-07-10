from fastapi import Request, APIRouter
from telegram import Update
from telegram.ext import Application
from telegram.constants import ParseMode
from telegram.constants import ChatAction
from langchain_core.messages import HumanMessage
import src.agent.workflow as workflow
from src.utils.command_handler import process_command
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

    command_result =await process_command(user_query, user_id)
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
        result = await workflow.get_workflow().ainvoke(
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
        print(f"Error in Telegram handler: {e}")
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text="*I encountered an issue processing your request.*\n\nPlease try again or visit : [IPS Academy IES ](https://ies.ipsacademy.org/) for information.",
            parse_mode=ParseMode.MARKDOWN,
        )
    return {"status": "ok"}

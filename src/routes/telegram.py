from fastapi import Request, APIRouter
from telegram import Update
from telegram.ext import Application
from telegram.constants import ParseMode
from telegram.constants import ChatAction
from langchain_core.messages import HumanMessage
from src.agent.workflow import wf
from src.utils.clear_history import clear_history
import os

TOKEN = os.getenv("TELEGRAM_ACCESS_TOKEN")
telegram_app = Application.builder().token(TOKEN).build()

telegram_router = APIRouter()


@telegram_router.post("/telegram")
async def telegram_webhook(request: Request):
    """Receive messages from Telegram"""
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    user_query: str = update.message.text
    user_id = update.effective_user.id

    if user_query.lower().strip() == "/clear":
        clear = clear_history(str(user_id))
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=clear["message"],
            parse_mode=ParseMode.MARKDOWN,
        )
        return {"status": "ok"}

    if user_query.lower().strip() == "/start":
        start_message = (
            "Welcome to the *IPS Campus Assistant*! 🤖\n\n"
            "I can help you with:\n"
            "• *Syllabus & study schemes*\n"
            "• *Portal Attendance* (needs computer code & password)\n"
            "• *Campus Updates & Placements*\n"
            "• *Academic Calendar & Schedules*\n"
            "• *Rules, Conduct & Brochure*\n"
            "• *Admission Procedure*\n\n"
            "*Commands:*\n"
            "• `/start` - Show this message\n"
            "• `/clear` - Clear conversation history\n\n"
            "What would you like to know? 😊"
        )
        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=start_message,
            parse_mode=ParseMode.MARKDOWN,
        )
        return {"status": "ok"}

    print("User- ", user_query)
    try:
        await telegram_app.bot.send_chat_action(
            chat_id=user_id,
            action=ChatAction.TYPING
        )
        result = await wf.ainvoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"configurable": {"thread_id": user_id}},
        )

        await telegram_app.bot.send_message(
            chat_id=user_id,
            text=result["messages"][-1].content,
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

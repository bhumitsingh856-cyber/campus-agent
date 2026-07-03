from src.utils.clear_history import clear_history
from src.utils.register_user import get_student, register, unregister
from src.utils.start_message import commands, start_message


async def process_command(user_query: str, chat_id: str) -> dict:
    query = user_query.strip()
    lower = query.lower()

    if lower.startswith("/register"):
        parts = query.split()
        if len(parts) != 3:
            return {
                "handled": True,
                "message": "*Usage: /register <Computer-code> <Password>*",
            }
        res =await register(parts[1], parts[2], str(chat_id))
        return {"handled": True, "message": res["message"]}

    if lower == "/help":
        return {"handled": True, "message": commands}

    if lower == "/start":
        return {"handled": True, "message": start_message}

    if lower == "/clear":
        clear =await clear_history(str(chat_id))
        return {"handled": True, "message": clear["message"]}

    if lower == "/profile":
        res =await get_student(str(chat_id))
        profile = ""
        if res.get("data"):
            data = res["data"]
            profile = (
                "*Student Primary Details*\n\n"
                f"Name : *{data.get('Name')}*\n"
                f"Computer Code : *{data.get('Computer Code')}*\n"
                f"DOB : *{data.get('Date of Birth')}*\n"
                f"Gender : *{data.get('Gender')}*\n"
                f"Enroll no. : *{data.get('Enrollment No.')}*\n"
                f"Course : *{data.get('Course')}*\n"
                f"Branch : *{data.get('Branch')}*\n"
                f"Year : *{data.get('Year')}*\n"
                f"Academic Session : *{data.get('Academic Session')}*\n"
                f"Mobile no. : *{data.get('Mobile No.')}*\n"
                f"Email : *{data.get('Email')}*\n"
            )
        return {"handled": True, "message": profile or res.get("message", "No profile available.")}

    if lower.startswith("/unregister"):
        res =await unregister(str(chat_id))
        return {"handled": True, "message": res["message"]}

    if query.startswith("/"):
        return {
            "handled": True,
            "message": "*Command does not exist, use /help to view available commands !*",
        }

    return {"handled": False}

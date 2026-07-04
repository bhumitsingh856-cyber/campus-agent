from src.agent.tools.tools import get_student_details
import src.db.checkpointer as db

async def register(computer_code: str, password: str, chat_id: str):
    namespace = ("student", chat_id)
    student = await db.store.aget(namespace, "profile")
    if student:
        return {"success": True, "message": "*Computer code is already registered ❗*"}

    data = get_student_details(computer_code, password)

    if not data["success"]:
        return data
    try:
        await db.store.aput(namespace, "profile", data["message"])
        return {"success": True, "message": "*Student registered successfully ✔️*"}
    except Exception as e:
        return {
            "success": False,
            "message": "*Unable to register student, please try again later ❌*",
        }


async def unregister(chat_id: str):
    namespace = ("student", chat_id)
    try:
        if not await db.store.aget(namespace, "profile"):
            return {
                "success": True,
                "message": "*No Computer Code found to unregister, please register first ❗*",
            }
        await db.store.adelete(namespace, "profile")
        return {"success": True, "message": "*Unregistered successfully ✔️*"}
    except Exception as e:
        return {
            "success": True,
            "message": "*Unable Unregister at this moment , please tyr again later ❌*",
        }


async def get_student(chat_id: str):
    namespace = ("student", chat_id)
    try:
        student = await db.store.aget(namespace, "profile")
        if student:
            return {"data": student.value}
        else:
            return {"message": "No student data exists❗", "data": None}
    except Exception as e:
        print(e)
        return {
            "message": "Unable to fetch student details, please try again later ❌",
            "data": None,
        }

from langgraph.store.memory import InMemoryStore
from src.agent.tools.tools import get_student_details

store = InMemoryStore()

def register(computer_code: str, password: str, chat_id: str):
    namespace = ("student", chat_id)
    student = store.get(namespace, "profile")
    if student:
        return {"success": True, "message": "*Computer code is already registered ❗*"}

    # data = get_student_details(computer_code, password)
    data = {
        "success": True,
        "message": {
            "Name": "BHUMIT SINGH",
            "Course": "B.Tech.",
            "Year": "2",
            "Academic Session": "2025-2026(Jan-June)",
            "Category": "SC",
            "Computer Code": "70010",
            "Gender": "M",
            "Blood Group": "A+",
            "Date of Birth": "18-03-2007",
            "Date Of Admission": "2024-12-20",
            "Mobile No.": "9826972085",
            "Email": "Sbhumit828@gmail.com",
            "Branch": "AIML",
            "Semester": "4",
            "Enrollment No.": "0808CL241048",
        },
    }
    if not data["success"]:
        return data
    try:
        store.put(namespace, "profile", data["message"])
        return {"success": True, "message": "*Student registered successfully ✔️*"}
    except Exception as e:
        return {
            "success": False,
            "message": "*Unable to register student, please try again later ❌*",
        }


def unregister(chat_id: str):
    namespace = ("student", chat_id)
    try:
        if not store.get(namespace, "profile"):
            return {
                "success": True,
                "message": "*No Computer Code found to unregister, please register first ❗*",
            }
        store.delete(namespace, "profile")
        return {"success": True, "message": "*Unregistered successfully ✔️*"}
    except Exception as e:
        return {
            "success": True,
            "message": "*Unable Unregister at this moment , please tyr again later ❌*",
        }


def get_student(chat_id: str):
    namespace = ("student", chat_id)
    try:
        student = store.get(namespace, "profile")
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

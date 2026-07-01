from src.agent.workflow import checkpoint

def clear_history(thread_id: str):
    try:
        if thread_id not in checkpoint.storage:
            return {"success": False, "message": "*Conversation history is empty❕*"}
        checkpoint.storage.pop(thread_id)
        return {
            "success": True,
            "message": "*Conversation memory cleared successfully ✔️*",
        }
    except Exception as e:
        return {
            "success": False,
            "message": "*Unable to delete Conversation memory, please try agin ❌*",
        }

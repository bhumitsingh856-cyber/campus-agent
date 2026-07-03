import src.db.checkpointer as db
async def clear_history(thread_id: str):
    try:
        checkpoints = [c async for c in db.checkpointer.alist(config={"configurable": {"thread_id": thread_id}})]
        print(checkpoints)
        if not checkpoints:
            return {"success": False, "message": "*Conversation history is empty❕*"}

        # To delete all history for a thread, use adelete_thread
        await db.checkpointer.adelete_thread(thread_id)

        return {
            "success": True,
            "message": "*Conversation memory cleared successfully ✔️*",
        }
    except Exception as e:
        print(e)
        return {
            "success": False,
            "message": "*Unable to delete Conversation memory, please try agin ❌*",
        }

from fastapi import APIRouter
from src.agent.workflow import wf
from src.utils.command_handler import process_command
from langchain_core.messages import HumanMessage

bot_router = APIRouter()


@bot_router.post("/bot")
async def bot(req: str, thread_id: str):
    command_result = process_command(req, thread_id)
    if command_result["handled"]:
        return command_result["message"]

    try:
        res = await wf.ainvoke(
            {"messages": [HumanMessage(content=req)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return res["messages"][-1].content
    except Exception as e:
        print(e)
        return "*Something went Wrong, Please try again later*"

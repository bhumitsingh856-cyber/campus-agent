from fastapi import APIRouter
import src.agent.workflow as workflow
from src.utils.command_handler import process_command
from langchain_core.messages import HumanMessage
from fastapi import Request

bot_router = APIRouter()


@bot_router.post("/bot")
async def bot(fetch_request: Request):
    data=await fetch_request.json()
    req=data.get("query")
    thread_id=data.get("thread_id")
    command_result =await process_command(req, thread_id)
    if command_result["handled"]:
        return command_result["message"]

    try:
        res = await workflow.get_workflow().ainvoke(
            {"messages": [HumanMessage(content=req)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return res["messages"][-1].content
    except Exception as e:
        print(f"Error in /bot endpoint: {e}")
        return "*I encountered an issue processing your request.*\n\nPlease try again or visit : [IPS Academy IES ](https://ies.ipsacademy.org/) for information."

from fastapi import APIRouter
from src.agent.workflow import wf
from langchain_core.messages import HumanMessage

bot_router = APIRouter()


@bot_router.post("/bot")
async def bot(req: str, thread_id: str):
    try:
        res = await wf.ainvoke(
            {"messages": [HumanMessage(content=req)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        return res["messages"][-1].content
    except Exception as e:
        print(e)
        return "*Something went Wrong, Please try again later*"

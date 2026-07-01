from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from src.agent.prompt.sys import SYSTEM_PROMPT
from src.agent.llm import llm
from src.agent.tools.tools import tools
from langgraph.prebuilt import tools_condition
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
import asyncio


class GlobalState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def chat(state: GlobalState):
    
    msg=trim_messages(
        messages=state['messages'],
        token_counter=count_tokens_approximately,
        max_tokens=7000,
        strategy="last"
    )
    res =await llm.bind_tools(tools).ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), *msg]
    )
    return {"messages": [res]}

toolnode = ToolNode(tools)

checkpoint = MemorySaver()

graph = StateGraph(GlobalState)

graph.add_node("tools", toolnode)
graph.add_node("chat", chat)

graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

wf = graph.compile(checkpointer=checkpoint)

# async def main():
#     while True:
#         a = input("User - ")
#         if a == "`":
#             break
#         async for i, j in wf.astream(
#             {"messages": [HumanMessage(content=a)]},
#             config={"configurable": {"thread_id": 0.11}},
#             stream_mode="messages",
#         ):
#             if isinstance(i, AIMessage):
#                 print(i.content, end="", flush=True)
#         print("\n...............................................................................")
# asyncio.run(main())
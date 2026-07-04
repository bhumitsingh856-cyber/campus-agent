from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from src.agent.prompt.sys import SYSTEM_PROMPT
from src.agent.llm import llm
from src.agent.tools.tools import tools
from langgraph.prebuilt import tools_condition
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

import src.db.checkpointer as db

from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
import asyncio

class GlobalState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def chat(state: GlobalState , config:RunnableConfig , store:BaseStore):
    thread_id=config['configurable']['thread_id']
    namespace=('student',str(thread_id))
    student=None
    try:
        student=await db.store.aget(namespace,"profile")
    except Exception as e:
        student=None
        
    # Trimming messages to manage context window 
    msg=trim_messages(
        messages=state['messages'],
        token_counter=count_tokens_approximately,
        max_tokens=7000,
        strategy="last",
        allow_partial=False,
        start_on=HumanMessage
    )
    prompt=SYSTEM_PROMPT
    if student:
        prompt+=f"\nStudent Details : {student.value}"
    try:
        
        res =await llm.bind_tools(tools).ainvoke(
            [SystemMessage(content=prompt), *msg]
        )
        return {"messages": [res]}
    except Exception as e:
        return {"messages": [AIMessage(content="*Assistant* encountered an issue processing your request.*\n\nPlease try again or visit : [IPS Academy IES ](https://ies.ipsacademy.org/) for information.")]}

toolnode = ToolNode(tools)


graph = StateGraph(GlobalState)

graph.add_node("tools", toolnode)
graph.add_node("chat", chat)

graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

wf = None

def get_workflow():
    global wf
    if wf is None:
        if db.checkpointer is None or db.store is None:
            raise RuntimeError(
                "Database must be initialized before compiling the workflow."
            )
        wf = graph.compile(checkpointer=db.checkpointer, store=db.store)
    return wf

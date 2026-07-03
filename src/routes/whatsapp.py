from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
import src.agent.workflow as workflow
from src.utils.command_handler import process_command
from langchain_core.messages import HumanMessage
from src.utils.start_message import start_message

whatsapp_router = APIRouter()


@whatsapp_router.post("/whatsapp-webhook")
async def whatsapp_webhook(req: Request):
    form = await req.form()
    threadId = form.get("WaId")
    body = form.get("Body")
    res = MessagingResponse()

    if body is None:
        return Response(content=str(res), media_type="application/xml")

    command_result =await process_command(body, threadId)
    if command_result["handled"]:
        res.message(command_result["message"])
        return Response(content=str(res), media_type="application/xml")

    try:
        agent_res = await workflow.get_workflow().ainvoke(
            {"messages": [HumanMessage(content=body)]},
            config={"configurable": {"thread_id": threadId}},
        )
        res.message(agent_res["messages"][-1].content)
        return Response(content=str(res), media_type="application/xml")
    except Exception as e:
        print(f"Error in WhatsApp handler: {e}")
        res.message("*I encountered an issue processing your request.*\n\nPlease try again or visit : [IPS Academy IES ](https://ies.ipsacademy.org/) for information.")
        return Response(content=str(res), media_type="application/xml")

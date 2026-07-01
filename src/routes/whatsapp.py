from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from src.agent.workflow import wf
from langchain_core.messages import HumanMessage
from src.utils.clear_history import clear_history

whatsapp_router = APIRouter()


@whatsapp_router.post("/whatsapp-webhook")
async def whatsapp_webhook(req: Request):
    form = await req.form()
    threadId = form.get("WaId")
    body = form.get("Body")
    res = MessagingResponse()

    if body.lower().strip() == "/clear":
        clear = clear_history(str(threadId))
        res.message(clear["message"])
        return Response(content=str(res), media_type="application/xml")
    if body.lower().strip() == "/start":
        start_message = (
            "Welcome to the *IPS Campus Assistant*! 🤖\n\n"
            "I can help you with:\n"
            "• *Syllabus & study schemes*\n"
            "• *Portal Attendance* (needs computer code & password)\n"
            "• *Campus Updates & Placements*\n"
            "• *Academic Calendar & Schedules*\n"
            "• *Rules, Conduct & Brochure*\n"
            "• *Admission Procedure*\n\n"
            "*Commands:*\n"
            "• `/start` - Show this message\n"
            "• `/clear` - Clear conversation history\n\n"
            "What would you like to know? 😊"
        )
        res.message(start_message)
        return Response(content=str(res), media_type="application/xml")
    try:
        agent_res = await wf.ainvoke(
            {"messages": [HumanMessage(content=body)]},
            config={"configurable": {"thread_id": threadId}},
        )
        res.message(agent_res["messages"][-1].content)
        return Response(content=str(res), media_type="application/xml")
    except Exception as e:
        print(e)
        res.message("*Something went, please try again later !*")
        return Response(content=str(res), media_type="application/xml")

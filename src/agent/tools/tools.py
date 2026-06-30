from langchain_core.tools import tool
from firecrawl import Firecrawl
from dotenv import load_dotenv
from src.db.vector import retriever
from langchain_tavily import TavilySearch, TavilyExtract
from typing import Literal

load_dotenv()
app = Firecrawl()
tavily = TavilySearch()
tavily_extract = TavilyExtract(extract_depth="basic", format="markdown")


@tool
async def get_attendence(computer_code: str, password: str):
    """Tools to get the attence of a student student"""
    try:
        result = await app.scrape(
            "https://cms2.ipsacademy.net/Login/sign_in", formats=["markdown"]
        )
        scrape_id = result.metadata.scrape_id
        await app.interact(
            scrape_id,
            prompt=f"login using computer code - {computer_code} , pass- {password}",
        )
        response = await app.interact(scrape_id, prompt="return the attendence")
        return response.output
    except Exception as e:
        return "Error while getting attendence,Try again later"


@tool
async def get_syllabus(
    course: Literal[
        "CSE-AIML",
        "CSE",
        "CS-IT",
        "CSE-DS",
    ],
):
    """Get syllabus link from IPS Academy. Searches official site only."""
    url=""
    if(course=="CSE"):
        url="https://ies.ipsacademy.org/departments/computer-science-engg/scheme-syllabus/"
    elif(course=="CSE-AIML"):
        url="https://ies.ipsacademy.org/departments/computer-science-engineering-artificial-intelligence-machine-learning/scheme-syllabus/"
    elif(course=="CSE-DS"):
        url="https://ies.ipsacademy.org/departments/scheme-syllabus-2/"
    elif(course=="CS-IT"):
        url="https://ies.ipsacademy.org/scheme-syllabus/"
    try:
        result = await tavily_extract.ainvoke(
            {"urls": [url]}
        )
        return result
    except Exception as e:
        return "Error while getting syllabus,Try again later"


@tool
async def admission_procedure():
    """Tool to get the admission procedure at institute"""
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/adminssion/admission-procedure/"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting admission procedure,Try again later"


@tool
async def institute_brochure(query: str):
    """Brochure contains information related to and about Institute"""
    try:
        docs =await retriever(query=query, namespace="campus")
        return docs
    except Exception as e:
        return "Error while getting institute brochure,Try again later"


@tool
async def code_of_conduct(query: str, whos: Literal["coc-student", "coc-employee"]):
    """Get the code of conduct of student and employee"""
    try:
        docs =await retriever(query=query, namespace=whos)
        return docs
    except Exception as e:
        return "Error while getting code of conduct,Try again later"


@tool
async def rules_regulations(query: str):
    """Get the rules and regulations of the institute"""
    try:
        docs =await retriever(query=query, namespace="rules-regulations")
        return docs
    except Exception as e:
        return "Error while getting rules and regulations,Try again later"


@tool
async def placements():
    """Tool to get the information regarding placements"""
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/training/"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting placements,Try again later"


# @tool
# async def upcoming_events():
#     """Use this tool to get the upcoming institute events"""
#     try:
#         result = await tavily_extract.ainvoke(
#             {"urls": ["https://ies.ipsacademy.org/category/upcoming/"]}
#         )
#         return result["results"][0]
#     except Exception as e:
#         return "Error while getting upcoming events,Try again later"


@tool
async def academic_programs(course: Literal["BE/BTech", "ME/MTech"]):
    """Get the Academic programs and courses provided by institute"""
    print("getting academic programs")
    url=""

    if(course=="BE/BTech"):
        url="https://ies.ipsacademy.org/academics/academic-programs/b-e"
    elif(course=="ME/MTech"):
        url="https://ies.ipsacademy.org/academics/academic-programs/m-e"

    try:
        result = tavily_extract.ainvoke(
            {"urls": [url]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting academic programs,Try again later"


@tool
async def scrape_url(url: str):
    """Tool to get the content of a pdf or scrape information from a webpage"""
    try:
        doc = await app.scrape(url, formats=["markdown"])
        return doc.markdown
    except Exception as e:
        return "Error while scraping the url,Try again later"


@tool
async def academic_calander():
    """Get the examination schedules and the academic calander"""
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/academics/academic-calendar"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting academic calander,Try again later"

@tool
async def get_campus_updates(category:Literal['notice-board','recent-news',"upcoming-events"]):
    """get the notice board , recent news , upcoming events of the institute"""

    url=""
    if(category=="notice-board"):
        url="https://ies.ipsacademy.org/category/notice-board/"
    elif(category=="recent-news"):
        url="https://ies.ipsacademy.org/category/recent/"
    elif(category=="upcoming-events"):
        url="https://ies.ipsacademy.org/category/upcoming/"

    try:
        result = await tavily_extract.ainvoke(
            {"urls": [url]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting notice board,Try again later"
@tool
async def get_department_schedule(dept:Literal[
    "computer-science",
    "",
])

tools = [
    get_attendence,
    get_syllabus,
    scrape_url,
    academic_calander,
    academic_programs,
    admission_procedure,
    institute_brochure,
    code_of_conduct,
    rules_regulations,
    placements,
]

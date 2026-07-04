from langchain_core.tools import tool
from firecrawl import Firecrawl
from dotenv import load_dotenv
from src.db.vector import retriever
from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.output_parsers import JsonOutputParser
from typing import Literal

load_dotenv()

app = Firecrawl()
tavily = TavilySearch()
tavily_extract = TavilyExtract(extract_depth="basic", format="markdown")
parser = JsonOutputParser()


@tool
async def get_attendence(computer_code: str, password: str):
    """Retrieves the attendance details for a student.

    Use this tool only when the user explicitly requests their attendance and
    provides their computer code and password. Do not call this tool without
    both credentials.

    Args:
        computer_code: The student's unique 5 digit computer code .
        password: The student's portal password / or DOB if available , formate: DD-MM-YYYY.

    Returns:
        A markdown-formatted string with attendance details or an error message.
    """
    print(f"Calling get_attendence for computer_code: {computer_code}")
    try:
        result = app.scrape(
            "https://cms2.ipsacademy.net/Login/sign_in", formats=["markdown"]
        )

        scrape_id = result.metadata.scrape_id
        sign_in = app.interact(
            scrape_id,
            prompt=f'SignIn using computer code: {computer_code} , password: {password} ,  return in JSON: {{"success":boolean,"message":"string"}}',
        )

        res = parser.parse(sign_in.output)
        print(res)
        if res and (not res.get("success")):
            app.stop_interaction(scrape_id)
            return res.get("details")

        response = app.interact(scrape_id, prompt="return the attendence")
        print(response.output)
        app.stop_interaction(scrape_id)
        return response.output
    except Exception as e:
        print(e)
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
    """Retrieves the official scheme and syllabus link/details for a specific branch.

    Use this tool when a user asks for the syllabus, scheme of study, or subject details
    for one of the supported engineering branches (CSE, CSE-AIML, CSE-DS, CS-IT).

    Args:
        course: The engineering branch name. Must be one of:
            - "CSE" (Computer Science & Engineering)
            - "CSE-AIML" (Artificial Intelligence & Machine Learning)
            - "CSE-DS" (Data Science)
            - "CS-IT" (Computer Science & Information Technology)

    Returns:
        The extracted syllabus information/link or an error message.
    """
    print(f"Calling get_syllabus for course: {course}")
    url = ""
    if course == "CSE":
        url = "https://ies.ipsacademy.org/departments/computer-science-engg/scheme-syllabus/"
    elif course == "CSE-AIML":
        url = "https://ies.ipsacademy.org/departments/computer-science-engineering-artificial-intelligence-machine-learning/scheme-syllabus/"
    elif course == "CSE-DS":
        url = "https://ies.ipsacademy.org/departments/scheme-syllabus-2/"
    elif course == "CS-IT":
        url = "https://ies.ipsacademy.org/scheme-syllabus/"
    try:
        result = await tavily_extract.ainvoke({"urls": [url]})
        return result
    except Exception as e:
        return "Error while getting syllabus,Try again later"


@tool
async def admission_procedure():
    """Retrieves the general admission procedure, criteria, and guidelines for the institute.

    Use this tool when the user asks how to get admission, eligibility criteria,
    application process, or general admission queries for the college.

    Returns:
        Details about the admission procedure or an error message.
    """
    print("Calling admission_procedure")
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/adminssion/admission-procedure/"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting admission procedure,Try again later"


@tool
async def institute_brochure(query: str):
    """Queries the local vector database of the institute brochure.

    The brochure contains official, detailed information about the institute's profile,
    infrastructure, facilities, courses offered, and general overview.
    Use this tool for queries seeking general information about the college facilities, history,
    or campus environment.

    Args:
        query: Semantic search query describing what details to look up in the brochure.

    Returns:
        Matching documents/passages from the brochure or an error message.
    """
    print(f"Calling institute_brochure with query: {query}")
    try:
        docs = await retriever(query=query, namespace="campus")
        return docs
    except Exception as e:
        return "Error while getting institute brochure,Try again later"


@tool
async def code_of_conduct(query: str, whos: Literal["coc-student", "coc-employee"]):
    """Queries the code of conduct documents for students or employees.

    Use this tool when the user asks about rules, ethics, duties, rights, behaviors,
    discipline policies, or code of conduct specific to students or employees.

    Args:
        query: Specific search query regarding the rule or code of conduct behavior.
        whos: Specifies whose code of conduct to query:
            - "coc-student": For student rules and guidelines.
            - "coc-employee": For faculty/staff code of conduct.

    Returns:
        Matching code of conduct passages or an error message.
    """
    print(f"Calling code_of_conduct for {whos} with query: {query}")
    try:
        docs = await retriever(query=query, namespace=whos)
        return docs
    except Exception as e:
        return "Error while getting code of conduct,Try again later"


@tool
async def rules_regulations(query: str):
    """Queries the rules and regulations document of the institute.

    Use this tool to find academic regulations, exam rules, passing criteria, attendance rules,
    detention policies, grading systems, and institutional guidelines.

    Args:
        query: Specific query regarding the institutional rules and regulations.

    Returns:
        Relevant sections of the rules and regulations document or an error message.
    """
    print(f"Calling rules_regulations with query: {query}")
    try:
        docs = await retriever(query=query, namespace="rules-regulations")
        return docs
    except Exception as e:
        return "Error while getting rules and regulations,Try again later"


@tool
async def placements():
    """Retrieves training and placement information, including recruiters, statistics, and career services.

    Use this tool when the user asks about placements, campus hiring, top recruiters,
    placement statistics, or training programs organized by the placement cell.

    Returns:
        Summary of placement details or an error message.
    """
    print("Calling placements")
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
    """Retrieves the details of undergraduate (BE/BTech) or postgraduate (ME/MTech) academic programs.

    Use this to get information about the streams, engineering disciplines, curriculum structure,
    or program details offered by the institute.

    Args:
        course: Program level. Must be "BE/BTech" for undergraduate or "ME/MTech" for postgraduate.

    Returns:
        Academic program details or an error message.
    """
    print(f"Calling academic_programs for course: {course}")
    url = ""

    if course == "BE/BTech":
        url = "https://ies.ipsacademy.org/academics/academic-programs/b-e"
    elif course == "ME/MTech":
        url = "https://ies.ipsacademy.org/academics/academic-programs/m-e"

    try:
        result = await tavily_extract.ainvoke({"urls": [url]})
        return result["results"][0]
    except Exception as e:
        return "Error while getting academic programs,Try again later"


@tool
async def scrape_url(url: str):
    """Scrapes content from a specific webpage or PDF URL.

    WARNING: Only use this tool when user *EXPLICITLY* asked for specific URL details to fetch (do not use this tool by yourself) . Do not guess
    or invent URLs. Use it to read page content or PDF instructions when given a valid URL.

    Args:
        STRICTLY NOT ALLOWED - url with jpeg/png or any image formate.
        url: The absolute HTTP/HTTPS URL of the webpage or PDF document to scrape.

    Returns:
        The markdown representation of the webpage/PDF content or an error message.
    """
    print(f"Calling scrape_url for url: {url}")
    try:
        doc = app.scrape(url, formats=["markdown"])
        return doc.markdown
    except Exception as e:
        print(e)
        return "Error while scraping the url,Try again later"


@tool
async def examination_schedules():
    """Retrieves the examination schedules like mid/end sem.

    Use this tool when users ask about semester dates, exam schedules.

    Returns:
        Examination details link or an error message.
    """
    print("Calling examination_schedules")
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/academics/academic-calendar"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting examination schedules,Try again later"


@tool
async def get_campus_updates(
    category: Literal["notice-board", "recent-news", "upcoming-events"],
):
    """Retrieves latest updates, announcements, notice board posts, recent news, or recruitment notices.

    Use this tool to get notice board notices, news updates, upcoming campus events,
    faculty/staff recruitment advertisements, or recent announcements.

    Args:
        category: The update category to fetch. Must be one of:
            - "notice-board": Official college notices, announcements, and general notices (including recruitment notices).
            - "recent-news": Recent news updates and press releases from the campus.
            - "upcoming-events": Upcoming events, workshops, seminars, and calendar events.

    Returns:
        Latest notices or news from the selected category or an error message.
    """
    print(f"Calling get_campus_updates for category: {category}")

    url = ""
    if category == "notice-board":
        url = "https://ies.ipsacademy.org/category/notice-board/"
    elif category == "recent-news":
        url = "https://ies.ipsacademy.org/category/recent/"
    elif category == "upcoming-events":
        url = "https://ies.ipsacademy.org/category/upcoming/"

    try:
        result = await tavily_extract.ainvoke({"urls": [url]})
        return result["results"][0]
    except Exception as e:
        return "Error while getting notice board,Try again later"


@tool
async def get_department_schedules(
    department: Literal[
        "civil",
        "chemical",
        "csit",
        "cse-ds",
        "computer-science",
        "cse-aiml",
        "cse-iot-csitcs",
        "electronics-communication",
        "elect-elex",
        "fire-tech",
        "mechanical",
        "general-eng",
    ],
):
    """Retrieves department-specific updates, re-exam schedules, and news.

    Use this tool when the query asks about , re-exams schedules, or news
    specific to a particular department (e.g., Civil, Chemical, Computer Science, etc.).

    Args:
        department: The specific engineering department. Must be one of:
            "civil", "chemical", "csit", "cse-ds", "computer-science", "cse-aiml",
            "cse-iot-csitcs", "electronics-communication", "elect-elex", "fire-tech",
            "mechanical", "general-eng".

    Returns:
        Departmental news/schedules or an error message.
    """
    print(f"Calling get_department_schedules for department: {department}")
    url = "https://ies.ipsacademy.org/category/"
    match department:
        case "civil":
            url += "civil"
        case "chemical":
            url += "chemical"
        case "mechanical":
            url += "mechanical"
        case "fire-tech":
            url += "fire-tech"
        case "computer-science" | "csit":
            url += "computer-science"
        case "cse-ds":
            url += "cse-ds"
        case "cse-aiml":
            url += "cse-aiml"
        case "cse-iot-csitcs":
            url += "cse-iot-csitcs"
        case "electronics-communication":
            url += "electronics-communication"
        case "elect-elex":
            url += "elect-elex"
        case "general-eng":
            url += "general-eng"
    try:
        result = await tavily_extract.ainvoke({"urls": [url]})
        return result["results"][0]
    except Exception as e:
        return "Error while getting department informatioans ,Try again later"


@tool
async def scholarship_notices():
    """Fetch latest scholarship notices from IPS Academy official website.

    Returns:
      Raw content from the scholarship notices page, or error message if unavailable."""
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/scholarship-notices"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting scholarship notices ,Try again later"


@tool
async def campus_facilities():
    """Fetch information about IPS Academy campus facilities and infrastructure.
    Returns:
       Facility details from the official website, or error message if unavailable.
    """
    try:
        result = await tavily_extract.ainvoke(
            {"urls": ["https://ies.ipsacademy.org/facilities/"]}
        )
        return result["results"][0]
    except Exception as e:
        return "Error while getting scholarship notices ,Try again later"


@tool
def academic_calender():
    """Retrieve the latest Academic calender for Btech/Mtech."""
    return "https://ies.ipsacademy.org/wp-content/uploads/2016/12/Academic-Calendar-AY-2026-27-B.Tech-M.Tech-IIyr-Onwards.pdf"



def get_student_details(computer_code: str, password: str):
    """Tool to register the student and get student details"""
    try:
        print("start")
        result = app.scrape(
            "https://cms2.ipsacademy.net/Login/sign_in", formats=["markdown"]
        )

        scrape_id = result.metadata.scrape_id
        sign_in = app.interact(
            scrape_id,
            prompt=f'SignIn using computer code: {computer_code} , password: {password} ,  return in JSON: {{"success":boolean,"message":"string"}}',
        )

        res = parser.parse(sign_in.output)
        if res and (not res.get("success")):
            app.stop_interaction(scrape_id)
            return res

        response = app.interact(
            scrape_id,
            prompt="From top right corner , select my profile , return all the primary information + Branch , semester , enroll no. , return a valid JSON only {'success':boolean,'message':{'key':'value'}}",
        )
        app.stop_interaction(scrape_id)
        return parser.parse(response.output)
    except Exception as e:
        print(e)
        return {
            "success": False,
            "message": "Unable to fetch the student details at the moment. Please try again.",
        }

tools = [
    get_attendence,
    get_syllabus,
    scrape_url,
    examination_schedules,
    academic_programs,
    admission_procedure,
    institute_brochure,
    code_of_conduct,
    rules_regulations,
    get_department_schedules,
    get_campus_updates,
    placements,
    scholarship_notices,
    campus_facilities,
    academic_calender,
]

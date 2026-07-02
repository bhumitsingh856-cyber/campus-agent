from langchain_openrouter import ChatOpenRouter
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cerebras import ChatCerebras

load_dotenv()

# llm = ChatCerebras(
#     model="gpt-oss-120b",
#     max_retries=2,
# )

llm = ChatCerebras(
    model="zai-glm-4.7",
)

# llm = ChatGroq(model="openai/gpt-oss-120b")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash")

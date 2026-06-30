from langchain_openrouter import ChatOpenRouter
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# llm = ChatGroq(model="openai/gpt-oss-120b")
llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct")

llm2 = ChatOpenRouter(
    model="openai/gpt-oss-120b:free",
)

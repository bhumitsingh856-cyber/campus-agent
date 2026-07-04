from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras
import os
load_dotenv()

llm = ChatCerebras(
    model=os.getenv("CEREBRAS_LLM"),
    max_retries=2,
)

# llm = ChatGroq(model="openai/gpt-oss-120b")

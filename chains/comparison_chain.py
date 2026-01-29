import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.comparison_prompt import comparison_prompt

load_dotenv()

def build_comparison_chain():
    llm = ChatOpenAI(
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.3,
    )

    chain = (
        comparison_prompt
        | llm
        | StrOutputParser()
    )

    return chain

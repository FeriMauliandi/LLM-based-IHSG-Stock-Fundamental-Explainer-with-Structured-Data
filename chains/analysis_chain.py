import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.fundamental_prompt import fundamental_prompt

load_dotenv()

def build_analysis_chain():
    llm = ChatOpenAI(
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.6,
    )

    chain = (
        fundamental_prompt
        | llm
        | StrOutputParser()
    )

    return chain



#"google/gemma-3-27b-it:free" == baguslah
# nvidia/nemotron-3-nano-30b-a3b:free

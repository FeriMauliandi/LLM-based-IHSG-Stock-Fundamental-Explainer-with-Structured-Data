import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.fundamental_prompt import fundamental_prompt
from prompts.comparison_prompt import comparison_prompt

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

#"google/gemma-3-27b-it:free" == baguslah
# nvidia/nemotron-3-nano-30b-a3b:free
# deepseek/deepseek-r1-0528:free
# meta-llama/llama-3.3-70b-instruct:free
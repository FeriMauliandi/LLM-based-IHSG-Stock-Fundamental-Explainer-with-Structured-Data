import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from prompts.fundamental_prompt import fundamental_prompt
from prompts.comparison_prompt import comparison_prompt

load_dotenv()

# List model OpenRouter yang dapat dicoba berurutan jika ada error/timeout
MODELS_TO_TRY = [
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openai/gpt-3.5-turbo"
]

def get_llm(model_name: str = None, temperature: float = 0.5):
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or "dummy"
    base_url = "https://openrouter.ai/api/v1" if os.getenv("OPENROUTER_API_KEY") else None

    selected_model = model_name or "google/gemma-2-9b-it:free"

    kwargs = {
        "model": selected_model,
        "temperature": temperature,
        "openai_api_key": api_key,
    }
    if base_url:
        kwargs["openai_api_base"] = base_url

    return ChatOpenAI(**kwargs)


class ResilientChain:
    """
    Chain pembungkus yang secara otomatis mencoba model cadangan jika model utama gagal.
    """
    def __init__(self, prompt, temperature=0.5):
        self.prompt = prompt
        self.temperature = temperature

    def invoke(self, inputs: dict) -> str:
        last_exception = None
        for model in MODELS_TO_TRY:
            try:
                llm = get_llm(model_name=model, temperature=self.temperature)
                chain = self.prompt | llm | StrOutputParser()
                return chain.invoke(inputs)
            except Exception as e:
                print(f"Model {model} gagal: {e}. Mencoba model berikutnya...")
                last_exception = e

        return f"Maaf, tidak dapat menghubungi model AI saat ini. Detail error: {last_exception}"


def build_analysis_chain():
    return ResilientChain(fundamental_prompt, temperature=0.5)

def build_comparison_chain():
    return ResilientChain(comparison_prompt, temperature=0.3)

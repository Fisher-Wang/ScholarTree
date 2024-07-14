import json
import os

import requests
from bs4 import BeautifulSoup
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from utils.common import extract_json_from_response, safe_get
from utils.crawler import get_webpage_content

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.deepseek.com",
    temperature=0.7,
    model_kwargs={"response_format": {"type": "json_object"}},
)

system_template = """
    You are a helpful assistant that extracts information about scholars.
"""

user_template = """
    Please extract the current affiliation of the scholar from the following text, ensuring that only the university name is provided (excluding institution or department names). If you can't find a clear affiliation, set it to null.

    Provide the output in the following JSON format:

    {{
        "affiliation": "Name of the university or company",
        "affiliation_abbreviated": "Abbreviated name of the affiliation",
        "confidence": "high/medium/low"
    }}

    Example output for a scholar affiliated with "Carnegie Mellon University School of Computer Science" should be:
    {{
        "affiliation": "Carnegie Mellon University",
        "affiliation_abbreviated": "CMU",
        "confidence": "high"
    }}

    Text:
    {text}
    """

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        ("user", user_template),
    ]
)

parser = StrOutputParser()
chain = prompt | llm | parser


def get_scholar_affiliation(url):
    text_content = get_webpage_content(url)
    if text_content:
        msg = chain.invoke({"text": text_content})
        data = extract_json_from_response(msg)
        return data.get("affiliation_abbreviated", None)
    else:
        return None


# Example usage
if __name__ == "__main__":
    # scholar_url = "https://hughw19.github.io/"
    scholar_url = "https://www.cs.cmu.edu/~abhinavg/"
    affiliation = get_scholar_affiliation(scholar_url)
    print(affiliation)

import asyncio
import json
import logging
from async_lru import alru_cache
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from robojudge.components.reasoning.llm_definitions import standard_llm

SYSTEM_MESSAGE_TEMPLATE = """\
Your task is to determine if a query/text is a valid query when searching for contents of civil court rulings (including family law).
You will receive a query and you should assess if it is related to something which could be decided by a civil court (e.g., family law, financial disputes, etc.).
Reject only the most obviously irrelevant queries.
If the query is irrelevant, provide a reasoning in Czech why.
{format_instructions}
Here is the query you should assess: {input}
"""


class QueryCheckerOutput(BaseModel):
    relevant: bool = Field(description='Is the query relevant')
    reasoning: str = Field(description='Why did you decide this way')


class RulingQueryChecker:
    MAX_INPUT = 500

    def __init__(self) -> None:
        output_parser = JsonOutputParser(pydantic_object=QueryCheckerOutput)
        prompt = PromptTemplate(template=SYSTEM_MESSAGE_TEMPLATE, input_variables=[
            'input'], partial_variables={'format_instructions': output_parser.get_format_instructions()})

        self.llm_chain = prompt | standard_llm | output_parser

    @alru_cache
    async def assess_query_relevance(self, query: str) -> dict:
        try:
            return await self.llm_chain.ainvoke(input={'input': query})
        except Exception as e:
            logging.exception(f'Error while assessing query relevance: {e}')


query_checker = RulingQueryChecker()

if __name__ == "__main__":
    question = "Kterým dopravním prostředkem jel žalovaný?"
    # question = "Rozvod manželů a péče svěřena jednomu z nich"

    res = asyncio.run(query_checker.assess_query_relevance(question))
    print(res)

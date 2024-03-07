import asyncio
import json
import logging
from async_lru import alru_cache

import openai

from robojudge.utils.settings import settings


SYSTEM_MESSAGE_TEMPLATE = """\
Your task is to determine if a query/text is a valid query when searching for contents of civil court curlings.
You will receive a query and you should assess if it is related to something which could be  decided by a civil court (e.g., family law, financial disputes, etc.).
If you are unsure, let the query pass.
If the query is irrelevant, provide a reasoning in Czech why.
Answer only with a JSON in the form `{"relevant": true/false, "reasoning": "your reasoning..."}`
"""

USER_MESSAGE_TEMPLATE = """
Decide if the query is related to something which could be found in a civil court ruling.
ALWAYS create your reasoning in Czech. Output ONLY JSON.
Here is the query you should assess: {input}
"""


class RulingQueryChecker:
    MAX_INPUT = 500

    @classmethod
    @alru_cache
    async def assess_query_relevance(cls, query: str) -> dict:
        openai.api_key = settings.OPENAI_API_KEY
        openai.api_base = settings.OPENAI_API_BASE

        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE_TEMPLATE},
            {
                "role": "user",
                "content": USER_MESSAGE_TEMPLATE.format(
                    input=query[:cls.MAX_INPUT]
                ),
            },
        ]

        try:
            chat_completion = openai.ChatCompletion.create(
                model=settings.GPT_MODEL_NAME, messages=messages, temperature=0
            )

            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            logging.exception(f'Error while assessing query relevance: {e}')


if __name__ == "__main__":
    question = "Kterým dopravním prostředkem jel žalovaný?"
    question = "Rozvod manželů a péče svěřena jednomu z nich"

    res = asyncio.run(RulingQueryChecker.assess_query_relevance(question))
    print(res)

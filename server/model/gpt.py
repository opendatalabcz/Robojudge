import asyncio

import openai

from server.utils.logger import logging
from server.utils.settings import settings
from server.utils.make_async import make_async

openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

# TODO: make async
# TODO: ignore poplatek a náklady řízení somehow somewhere
# TODO: give references to answers
SYSTEM_MESSAGE = (
    "You are a legal assistant who summarizes the provided court ruling. "
    "Extract the main factual and legal information. Ignore anonymized fields marked with square brackets '[...]'. "
    "Ignore information about 'soudní poplatek' and 'náklady řízení'. "
    "Answer only in Czech."
)


class OpenAIPrompter:
    @staticmethod
    def summarize_case(case_reasoning: str):
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": f'Summarize this court decision in a professional style: {case_reasoning}'}
        ]

        try:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, request_timeout=30)

            return chat_completion.choices[0].message.content
        except Exception:
            logger.exception("Exception while calling OpenAI API:")

        return ''

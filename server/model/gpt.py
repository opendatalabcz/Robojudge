import asyncio

import openai

from server.utils.logger import logging
from server.utils.settings import settings
from server.utils.make_async import make_async

openai.api_key = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

# TODO: make async
# TODO: retry logic
# TODO: try GPT-4
SYSTEM_MESSAGE = (
    "You are a legal assistant who summarizes the provided court ruling. "
    "Summarize what the case was about. Ignore anonymized fields marked with square brackets '[...]'. "
    "Ignore information about any administrative fees and legal costs reimbursement."
    "Answer only in Czech."
)


class OpenAIPrompter:
    @staticmethod
    def summarize_case(case_reasoning: str):
        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": f'Summarize what this court decision was about as a legal professional, but do not mention any administrative fees and legal costs reimbursement. Use 5-10 sentences: {case_reasoning}'}
        ]

        try:
            chat_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, request_timeout=30)

            return chat_completion.choices[0].message.content
        except Exception:
            logger.exception("Exception while calling OpenAI API:")

        return ''

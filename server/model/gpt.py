import openai

from utils.logger import logging

# TODO: Move to ENV
openai.api_key = "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"

logger = logging.getLogger(__name__)

# TODO: ignore poplatek a náklady řízení somehow somewhere
# TODO: give references to answers
SYSTEM_MESSAGE = (
    "You are a legal assistant who summarizes the provided court ruling."
    "Extract the main factual and legal information"
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

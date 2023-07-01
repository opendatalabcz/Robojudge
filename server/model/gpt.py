import openai

from utils.logger import logging

openai.api_key = "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"

logger = logging.getLogger(__name__)

# TODO: give references to answers
SYSTEM_MESSAGE = (
    "You are a legal assistant who summarizes the provided court ruling."
    "Extract the main factual and legal information"
    "Answer only in Czech."
)


class OpenAIPrompter:
    @staticmethod
    def summarize_case(case_reasoning: str):
        messages = {
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": f'Summarize the main arguments and points of this court decision: {case_reasoning}'}
        }

        try:
            chat_completion = openai.ChatCompletion.create(
                model="chatgpt", messages=messages, request_timeout=30)

            return chat_completion.choices[0].message.content
        except Exception:
            logger.exception("Exception while calling OpenAI API")

        return ''

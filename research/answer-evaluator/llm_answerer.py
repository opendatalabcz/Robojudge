import asyncio
from types import SimpleNamespace

from Bard import AsyncChatbot
from llama_cpp import Llama

from robojudge.utils.settings import settings
from robojudge.utils.logger import logging
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer

class LLM_TYPES(SimpleNamespace):
    LLM_TYPE_BARD = 'bard'
    LLM_TYPE_GPT = 'gpt'
    LLM_TYPE_LLAMA = 'llama'


BARD_ANSWER_PROMPT = """
You are a legal assistant who answers a question based on the provided text.
Create the answer ONLY in Czech!
Text: {text}
Question: {question}
"""

class ResearchLLMAnswerer:
    @classmethod
    async def generate_answer(cls, llm_type: str, question: str, text: str):
        if llm_type ==LLM_TYPES.LLM_TYPE_GPT:
            return await CaseQuestionAnswerer.answer_question(question, text)
        elif llm_type == LLM_TYPES.LLM_TYPE_BARD:
            return await cls.answer_bard(question, text)
        elif llm_type == LLM_TYPES.LLM_TYPE_LLAMA:
            return cls.answer_llama(question, text)

    @classmethod
    async def answer_bard(cls, question: str, text: str):
        try:
            llm_instance = await AsyncChatbot(settings.BARD__Secure_1PSID, settings.BARD__Secure_1PSIDTS)
            res = await llm_instance.ask(BARD_ANSWER_PROMPT.format(text=text, question=question))

            return res['content']
        except Exception:
            logging.exception("Exception while calling Bard API:")

        return ""

    @classmethod
    def answer_llama(cls, question: str, text: str):
        ...

if __name__ == '__main__':
    llm = Llama(model_path="./models/7B/llama-model.gguf")
    output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=True)
    print(output)
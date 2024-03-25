import replicate
import cohere

from robojudge.utils.settings import settings
from robojudge.components.reasoning.answerer import CaseQuestionAnswerer

LLM_TYPE_GPT = "gpt"
LLM_TYPE_GPT_FINETUNED = "gpt-custon"
LLM_TYPE_LLAMA = "llama"
LLM_TYPE_COHERE = "cohere"
LLM_TYPE_VICUNA = "vicuna"

MEASURED_LLM_TYPES = [LLM_TYPE_GPT_FINETUNED]

CUSTOM_LLM_NAME = "ft:gpt-3.5-turbo-1106:personal:002:96i5C6q4"

LLAMA_SYSTEM_PROMPT = """
You are a legal assistant who answers a question based on the provided text.
Return only the answer itself.
Create the answer ONLY in Czech!
"""

LLAMA_PROMPT = """
Text: {text}
Question: {question}
"""

COHERE_PROMPT = """
You are a legal assistant who answers a question based on the provided text.
Text: {text}
Question: {question}
Create the answer ONLY in Czech! Answer:
"""

VICUNA_PROMPT = """
Answer the question based on the provided text as a legal assistant.
Answer in Czech only!
Text: {text}
Question: {question}
The answer in Czech is:
"""


class ResearchLLMAnswerer:
    @classmethod
    async def generate_answer(cls, llm_type: str, question: str, text: str):
        if llm_type == LLM_TYPE_GPT:
            return await CaseQuestionAnswerer.answer_question(question, text)
        elif llm_type == LLM_TYPE_GPT_FINETUNED:
            return await CaseQuestionAnswerer.answer_question(question, text, CUSTOM_LLM_NAME)
        elif llm_type == LLM_TYPE_LLAMA:
            return cls.answer_llama(question, text)
        elif llm_type == LLM_TYPE_COHERE:
            return cls.answer_cohere(question, text)
        elif llm_type == LLM_TYPE_VICUNA:
            return cls.answer_vicuna(question, text)
        else:
            raise Exception(
                f'Unknown llm_type to generate an answer "{llm_type}"')

    @classmethod
    def answer_cohere(cls, question: str, text: str):
        co = cohere.Client(settings.COHERE_API_TOKEN)

        response = co.generate(
            prompt=COHERE_PROMPT.format(question=question, text=text),
        )
        print(response[0])
        return response[0]

    @classmethod
    def answer_llama(cls, question: str, text: str):
        output = replicate.run(
            "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            input={
                "system_prompt": LLAMA_SYSTEM_PROMPT,
                "prompt": LLAMA_PROMPT.format(question=question, text=text),
            },
        )

        result = "".join(list(output))
        return result

    @classmethod
    def answer_vicuna(cls, question: str, text: str):
        output = replicate.run(
            "replicate/vicuna-13b:6282abe6a492de4145d7bb601023762212f9ddbbe78278bd6771c8b3b2f2a13b",
            input={
                "prompt": VICUNA_PROMPT.format(question=question, text=text),
                "temperature": 0.25,
            },
        )

        result = "".join(list(output))
        return result


if __name__ == "__main__":
    ...

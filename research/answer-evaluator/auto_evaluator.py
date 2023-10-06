import logging

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

from robojudge.utils.settings import settings, standard_llm


COMPARE_SYSTEM_MESSAGE = """
Your task is to determine if a candidate answer is correct by comparing it to the correct answer.
The candidate answer does not have to have the same wording, but it should include the same information as the correct answer.
If the candidate answer is correct, output 1, otherwise output 0. Do not output anything else.
"""


class AutoEvaluator:
    @classmethod
    async def get_score_for_llm_type(
        cls, llm_answers: dict[str, str], human_answers: dict[str, str]
    ):
        logging.info("Auto-evaluating llm answers.")

        total_score = 0

        for file_name, llm_answer in llm_answers.items():
            try:
                human_answer = human_answers[file_name]

                result = await cls.compare_human_llm_answers(
                    human_answer=human_answer, llm_answer=llm_answer
                )

                total_score += int(result)

            except Exception:
                logging.exception(
                    f'Error while evaluating llm answer "{llm_answer}" in "{file_name}".'
                )

        return total_score

    @classmethod
    async def compare_human_llm_answers(cls, human_answer: str, llm_answer: str):
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            COMPARE_SYSTEM_MESSAGE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            """
            Correct answer: {human_answer}
            Candidate answer: {llm_answer}
            """
        )

        initial_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        llm_chain = LLMChain(llm=standard_llm, prompt=initial_prompt)

        return await llm_chain.arun(human_answer=human_answer, llm_answer=llm_answer)

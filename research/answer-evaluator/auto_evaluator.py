import logging
import asyncio

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain

from robojudge.utils.settings import settings, advanced_llm


COMPARE_SYSTEM_MESSAGE = """
Your task is to score a candidate answer based on how similar it is to the correct answer.
The candidate answer does not have to have the same wording, but it should include the same information as the correct answer.
Give 0 to 10 points to the candidate answer based on how useful and relevant it is (compared to the correct answer).
Output ONLY the number of points, for example: "6".
"""


class AutoEvaluator:
    @classmethod
    async def get_score_for_llm_type(
        cls, llm_answers: dict[str, str], human_answers: dict[str, str], llm_type: str
    ):
        logging.info(f"Auto-evaluating llm answers for '{llm_type}'.")

        output = {}

        comparison_requests = []
        comparison_file_names = []
        for file_name, llm_answer in llm_answers.items():
            human_answer = human_answers[file_name]
            comparison_file_names.append(file_name)
            comparison_requests.append(
                cls.compare_human_llm_answers(
                    human_answer=human_answer, llm_answer=llm_answer
                )
            )

        try:
            results = await asyncio.gather(*comparison_requests)

            # Prevent circular ipmort
            from base_evaluator import ScoreResult

            for file_name, result in zip(comparison_file_names, results):
                output[file_name] = ScoreResult(
                    human_answer=human_answer, llm_answer=llm_answer, score=result
                )

        except Exception:
            logging.exception(
                f'Error while evaluating llm answer "{llm_answer}" in "{file_name}".'
            )

        return output

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

        llm_chain = LLMChain(llm=advanced_llm, prompt=initial_prompt)

        return await llm_chain.arun(human_answer=human_answer, llm_answer=llm_answer)


if __name__ == "__main__":
    human_answers = {
        "1": "Vyhrála žalobykně, byť jen částečně (soud část žaloby zamítl).",
        "2": "Vyhrála žalobykně, byť jen částečně (soud část žaloby zamítl).",
    }
    llm_answers = {
        "1": "Žalobkyně vyhrála tento soudní spor.",
        "2": "Žalobkyně vyhrála tento soudní spor.",
    }
    res = asyncio.run(
        AutoEvaluator.get_score_for_llm_type(
            llm_answers=llm_answers, human_answers=human_answers, llm_type="llama"
        )
    )
    print(res)

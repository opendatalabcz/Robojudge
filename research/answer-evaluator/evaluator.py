import asyncio
from pathlib import Path
import datetime

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import RefineDocumentsChain, LLMChain

from llm_answerer import ResearchLLMAnswerer, LLM_TYPES
from robojudge.utils.settings import settings, standard_llm

ANSWER_FILE_SEPARATOR = '<SEP>'
BASE_ANSWERS_PATH = Path('datasets/answer-evaluation/')
HUMAN_ANSWERS_PATH = BASE_ANSWERS_PATH / 'reference'

BASE_SCORES_PATH = Path('results/answer-evaluation/')

COMPARE_SYSTEM_MESSAGE = """
Your task is to determine if a candidate answer is correct by comparing it to the correct answer.
The candidate answer does not have to have the same wording, but it should include the same information as the correct answer.
If the candidate answer is correct, output 1, otherwise output 0. Do not output anything else.
"""


class Evaluator:
    def __init__(self) -> None:
        self.human_answers = {}
        for reference_file_path in HUMAN_ANSWERS_PATH.iterdir():
            self.human_answers[reference_file_path.name] = reference_file_path.read_text(
            )

    async def generate_llm_answer_summaries(self):
        for llm_type in dict(LLM_TYPES).values:
            (BASE_SCORES_PATH / llm_type).mkdir(parents=True, exist_ok=True)
            scores = await self.evaluate_llm_answers(llm_type)
            score_path: Path = BASE_SCORES_PATH / llm_type / f'score_{datetime.datetime.strftime("%Y-%m-%d")}'
            score_path.write_text(scores)

    async def evaluate_llm_answers(self, llm_type: str):
        (BASE_ANSWERS_PATH / llm_type).mkdir(parents=True, exist_ok=True)
        answer_scores = {}

        for human_answer_file_name, human_answer_text in self.human_answers.items():
            question_text, question, human_answer = human_answer_text.split(ANSWER_FILE_SEPARATOR)
            llm_answer_path: Path = BASE_ANSWERS_PATH / llm_type / human_answer_file_name
            if not Path.exists(llm_answer_path):
                llm_answer = await ResearchLLMAnswerer.generate_answer(llm_type, question=question, text=question_text)
                llm_answer_path.write_text(llm_answer)
            else:
                llm_answer = llm_answer_path.read_text()

            answer_score = await self.compare_human_llm_answers(human_answer, llm_answer)
            answer_scores[question] = answer_score
        
        return answer_scores
            
    async def compare_human_llm_answers(self, human_answer: str, llm_answer: str):
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            COMPARE_SYSTEM_MESSAGE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            f"Correct answer: {human_answer}"
            f"Candidate answer: {llm_answer}"
        )

        initial_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        llm_chain = LLMChain(llm=standard_llm, prompt=initial_prompt)

        return await llm_chain.arun()


if __name__ == '__main__':
    evaluator = Evaluator()

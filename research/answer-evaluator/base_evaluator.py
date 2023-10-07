import asyncio
from pathlib import Path
import logging
from typing import Optional
import datetime
import csv

from pydantic import BaseModel

from auto_evaluator import AutoEvaluator
from bert_score_evaluator import BertScoreEvaluator
from llm_answerer import MEASURED_LLM_TYPES, ResearchLLMAnswerer

ANSWER_FILE_SEPARATOR = "<SEP>"
HUMAN_ANSWERS_PATH = Path("datasets/answering/reference")
BASE_RESULTS_PATH = Path("research/llm-answer-results/")
BASE_LLM_ANSWERS_PATH = BASE_RESULTS_PATH / "llm-answers"
BASE_LLM_SUMMARY_PATH = BASE_RESULTS_PATH / "summaries"


class ScoreResult(BaseModel):
    question: Optional[str] = ""
    human_answer: str
    llm_answer: str
    score: str


class BaseEvaluator:
    def __init__(self) -> None:
        self.llm_answers = {}
        self.reference_files = {}
        self.human_answers = {}
        self.reference_texts = {}
        self.reference_questions = {}

        for reference_file_path in HUMAN_ANSWERS_PATH.iterdir():
            self.reference_files[
                reference_file_path.name
            ] = reference_file_path.read_text()

            (
                text,
                question,
                human_answer,
            ) = reference_file_path.read_text().split(ANSWER_FILE_SEPARATOR)
            self.human_answers[reference_file_path.name] = human_answer
            self.reference_texts[reference_file_path.name] = text
            self.reference_questions[reference_file_path.name] = question

    async def run_overall_evaluation(self):
        await self.generate_llm_answers()

        for llm_type in MEASURED_LLM_TYPES:
            logging.info(f'Generating evaluation summary for "{llm_type}".')
            evaluation_summary_path: Path = (
                BASE_LLM_SUMMARY_PATH / datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
            )
            evaluation_summary_path.mkdir(parents=True, exist_ok=True)

            # llm_auto_score = await AutoEvaluator.get_score_for_llm_type(
            #     llm_answers=self.llm_answers[llm_type],
            #     human_answers=self.human_answers,
            #     llm_type=llm_type,
            # )
            # for file_name, result in llm_auto_score.items():
            #     result.question = self.reference_questions[file_name]
            # self.save_score_results(
            #     results=llm_auto_score,
            #     path=evaluation_summary_path / f"{llm_type}_llm_auto_score.csv",
            # )

            # bert_score = BertScoreEvaluator.get_score_for_llm_type(
            #     llm_answers=self.llm_answers[llm_type],
            #     human_answers=self.human_answers,
            #     llm_type=llm_type,
            # )
            # for file_name, result in bert_score.items():
            #     result.question = self.reference_questions[file_name]
            # self.save_score_results(
            #     results=bert_score,
            #     path=evaluation_summary_path / f"{llm_type}_bert_score.csv",
            # )

    async def generate_llm_answers(self):
        logging.info("Generating missing LLM answers.")
        for llm_type in MEASURED_LLM_TYPES:
            logging.info(f'Generating missing LLM answers for "{llm_type}".')
            (BASE_LLM_ANSWERS_PATH / llm_type).mkdir(parents=True, exist_ok=True)
            self.llm_answers[llm_type] = {}

            for file_name in self.human_answers:
                try:
                    llm_answer_path: Path = BASE_LLM_ANSWERS_PATH / llm_type / file_name
                    if not Path.exists(llm_answer_path):
                        llm_answer = await ResearchLLMAnswerer.generate_answer(
                            llm_type,
                            question=self.reference_questions[file_name],
                            text=self.reference_texts[file_name],
                        )
                        llm_answer_path.write_text(llm_answer)
                    else:
                        logging.info(
                            f'Answer for "{file_name}" and llm "{llm_type}" already exists.'
                        )
                        llm_answer = llm_answer_path.read_text()

                    self.llm_answers[llm_type][file_name] = llm_answer
                except Exception:
                    logging.exception(
                        f'Error while generating LLM answer for question in "{file_name}".'
                    )

    @classmethod
    def save_score_results(cls, results: dict[str, ScoreResult], path: Path):
        with open(path, "w") as file:
            writer = csv.writer(
                file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            writer.writerow(
                [
                    "file_name",
                    "question",
                    "human_answer",
                    "llm_answer",
                    "score",
                ]
            )

            for file_name, result in results.items():
                writer.writerow(
                    [
                        file_name,
                        result.question,
                        result.human_answer,
                        result.llm_answer,
                        result.score,
                    ]
                )


if __name__ == "__main__":
    evaluator = BaseEvaluator()
    asyncio.run(evaluator.run_overall_evaluation())

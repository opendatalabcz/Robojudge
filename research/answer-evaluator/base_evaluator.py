import asyncio
from pathlib import Path
import logging
import datetime

from auto_evaluator import AutoEvaluator
from bert_score_evaluator import BertScoreEvaluator
from llm_answerer import LLM_TYPES, ResearchLLMAnswerer

ANSWER_FILE_SEPARATOR = "<SEP>"
HUMAN_ANSWERS_PATH = Path("datasets/answering/reference")
BASE_RESULTS_PATH = Path("research/llm-answer-results/")
BASE_LLM_ANSWERS_PATH = BASE_RESULTS_PATH / "llm-answers"
BASE_LLM_SUMMARY_PATH = BASE_RESULTS_PATH / "summaries"


class BaseEvaluator:
    def __init__(self) -> None:
        self.llm_answers = {}
        self.human_answers = {}
        for reference_file_path in HUMAN_ANSWERS_PATH.iterdir():
            self.human_answers[
                reference_file_path.name
            ] = reference_file_path.read_text()

    async def run_overall_evaluation(self):
        await self.generate_llm_answers()

        for llm_type in LLM_TYPES:
            logging.info(f'Generating evaluation summary for "{llm_type}".')
            evaluation_summary_path: Path = (
                BASE_LLM_SUMMARY_PATH
                / llm_type
                / f'score_{datetime.datetime.now().strftime("%Y-%m-%d")}'
            )

            # TODO: Formatting
            llm_auto_score = await AutoEvaluator.get_score_for_llm_type(
                llm_answers=self.llm_answers[llm_type], human_answers=self.human_answers
            )

            bert_score = BertScoreEvaluator.get_score_for_llm_type(
                llm_answers=self.llm_answers[llm_type], human_answers=self.human_answers
            )

            # evaluation_summary_path.write_text(llm_auto_score)

    async def generate_llm_answers(self):
        logging.info("Generating missing LLM answers.")
        for llm_type in LLM_TYPES:
            (BASE_LLM_ANSWERS_PATH / llm_type).mkdir(parents=True, exist_ok=True)
            self.llm_answers[llm_type] = {}

            for human_answer_file_name, human_answer_text in self.human_answers.items():
                question_text, question, human_answer = human_answer_text.split(
                    ANSWER_FILE_SEPARATOR
                )

                try:
                    llm_answer_path: Path = (
                        BASE_LLM_ANSWERS_PATH / llm_type / human_answer_file_name
                    )
                    if not Path.exists(llm_answer_path):
                        llm_answer = await ResearchLLMAnswerer.generate_answer(
                            llm_type, question=question, text=question_text
                        )
                        llm_answer_path.write_text(llm_answer)
                    else:
                        llm_answer = llm_answer_path.read_text()
                        
                    self.llm_answers[llm_type][human_answer_file_name] = llm_answer
                except Exception:
                    logging.exception(
                        f'Error while generating LLM answer for "{human_answer_file_name}".'
                    )

                # TODO: testing one case
                break

if __name__ == '__main__':
    evaluator = BaseEvaluator()
    asyncio.run(evaluator.run_overall_evaluation())
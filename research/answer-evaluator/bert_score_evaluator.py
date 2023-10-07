import logging
from pathlib import Path
import csv

from evaluate import load


class BertScoreEvaluator:
    @classmethod
    def get_score_for_llm_type(
        cls, llm_answers: dict[str, str], human_answers: dict[str, str], llm_type: str
    ):
        logging.info(f"Bert-Score evaluating llm answers '{llm_type}'.")
        bertscore = load("bertscore")

        # Ensure the same order before batch evaluation by Bert-Score
        file_names = []
        human_answer_list = []
        llm_answer_list = []
        for file_name, llm_answer in llm_answers.items():
            file_names.append(file_name)
            llm_answer_list.append(llm_answer)
            human_answer_list.append(human_answers[file_name])

        results = bertscore.compute(
            predictions=llm_answer_list,
            references=human_answer_list,
            model_type="bert-base-multilingual-cased",
        )

        # Prevent circular import
        from base_evaluator import ScoreResult

        output = {}
        for file_name, f1, human_answer, llm_answer in zip(
            file_names, results["f1"], human_answer_list, llm_answer_list
        ):
            output[file_name] = ScoreResult(
                human_answer=human_answer, llm_answer=llm_answer, score=f1
            )
        return output

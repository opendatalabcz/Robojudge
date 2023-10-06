import logging

from evaluate import load


class BertScoreEvaluator:
    @classmethod
    def get_score_for_llm_type(
        cls, llm_answers: dict[str, str], human_answers: dict[str, str]
    ):
        logging.info("Bert-Score evaluating llm answers.")
        bertscore = load("bertscore")

        # Ensure the same order before batch evaluation by Bert-Score
        human_answer_list = []
        llm_answer_list = []
        for file_name, llm_answer in llm_answers.items():
            llm_answer_list.append(llm_answer)
            human_answer = human_answers[file_name]
            human_answer_list.append(human_answer)

        result = bertscore.compute(
            predictions=llm_answer_list,
            references=human_answer_list,
            model_type="bert-base-multilingual-cased",
        )

        print(result)
        return result

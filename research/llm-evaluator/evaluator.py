from pathlib import Path
import logging

import evaluate


REFERENCE_SUMMARY_PATH = Path('datasets/llm-summary-testing/reference')


class Evaluator:
    def __init__(self) -> None:
        self.rouge_score = evaluate.load('rouge')
        self.reference_summaries = {}
        for reference_summary_path in REFERENCE_SUMMARY_PATH.iterdir():
            self.reference_summaries[reference_summary_path.name] = reference_summary_path.read_text(
            )

    def compute_rouge_score(self, generated_summary_path: Path):
        reference_summaries = []
        generated_summaries = []
        for generated_summary_path in generated_summary_path.iterdir():
            summary_name = generated_summary_path.name
            reference_summary = self.reference_summaries.get(summary_name, '')
            
            if not reference_summary:
                logging.warn(
                    f'Could not find reference summary for "{summary_name}", skipping.')
                continue

            reference_summaries.append(reference_summary)
            generated_summaries.append(generated_summary_path.read_text())

        scores = self.rouge_score.compute(
            predictions=generated_summaries, references=reference_summaries)

        return scores

    def evaluate_summaries(self, generated_summary_path: str):
        scores = self.compute_rouge_score(Path(generated_summary_path))
        print(scores)


if __name__ == '__main__':
    evaluator = Evaluator()
    evaluator.evaluate_summaries('datasets/llm-summary-testing/gpt3')

from pathlib import Path
import json

from robojudge.components.reasoning.answerer import SYSTEM_MESSAGE_TEMPLATE

ANSWER_FILE_SEPARATOR = "<SEP>"
HUMAN_EVALUATED_ANSWERS_REFERENCE_PATH = Path("datasets/answering/reference")
AUTO_EVALUATED_ANSWERS_REFERENCE_PATH = Path(
    "datasets/answering/only-auto-evaluation-reference")

TRAIN_DATASET_PATH = Path('datasets/finetuning/train.jsonl')
TEST_DATASET_PATH = Path('datasets/finetuning/test.jsonl')


def create_jsonl_dataset(path: Path):
    lines = []
    for reference_file_path in path.iterdir():
        (
            text,
            question,
            human_answer,
        ) = reference_file_path.read_text().split(ANSWER_FILE_SEPARATOR)
        line = {"messages": [{
            "role": "system", "content": SYSTEM_MESSAGE_TEMPLATE
        }, {"role": "user", "content":             f"Question: {question}\nTry to answer the question based on the initial court ruling part: {text}"
            }, {"role": "assistant", "content": human_answer}]}

        lines.append(line)

    return lines


def create_datasets():

    train_lines = create_jsonl_dataset(AUTO_EVALUATED_ANSWERS_REFERENCE_PATH)
    with TRAIN_DATASET_PATH.open('w') as wf:
        for line in train_lines:
            wf.write(json.dumps(line) + '\n')

    test_lines = create_jsonl_dataset(HUMAN_EVALUATED_ANSWERS_REFERENCE_PATH)
    with TEST_DATASET_PATH.open('w') as wf:
        for line in test_lines:
            wf.write(json.dumps(line) + '\n')


if __name__ == '__main__':
    create_datasets()

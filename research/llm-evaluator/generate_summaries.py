from pathlib import Path
import asyncio
import concurrent.futures
import time

from robojudge.components.summarizer.base_summarizer import BaseSummarizer
from robojudge.components.summarizer.gpt_summarizer import GPTSummarizer
from robojudge.components.summarizer.llama_summarizer import LlamaSummarizer
from robojudge.components.summarizer.bard_summarizer import BardSummarizer
from robojudge.utils.logger import logging
from robojudge.utils.settings import settings

logger = logging.getLogger(__name__)

OUTPUT_BASE_PATH = 'datasets/llm-summary-testing/unified-summaries'
WORKERS = 1


class SummaryGenerator:
    def __init__(self, input_dir: str, llm: str = settings.DEFAULT_SUMMARIZE_LLM) -> None:
        self.input_texts = {}
        for input_file in Path(input_dir).iterdir():
            self.input_texts[input_file.name] = input_file.read_text()

        self.llm = llm
        (Path(OUTPUT_BASE_PATH)/self.llm).mkdir(parents=True, exist_ok=True)

    def generate_summaries(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            executor.map(self.generate_summary, self.input_texts.items())

    def generate_summary(self, input_params):
        try:
            file_name, text = input_params
            start = time.perf_counter()
            summarizer = self.choose_summarizer()(text=text, file_name=file_name)
            summary = asyncio.run(summarizer.summarize_text(
                cache_chunks=True, cache_chunk_summaries=True, create_overall_summary=False))
            logger.info(
                f'Summarizing "{file_name}" with {self.llm} with {self.llm} took {time.perf_counter() - start} seconds')

            output_path = Path(OUTPUT_BASE_PATH) / self.llm / file_name
            output_path.write_text(summary)
        except Exception:
            logger.exception(
                f'Error while summarizing "{file_name}" with {self.llm}:')

    def choose_summarizer(self) -> BaseSummarizer:
        if self.llm == 'llama':
            return LlamaSummarizer
        elif self.llm == 'bard':
            return BardSummarizer
        else:
            return GPTSummarizer


if __name__ == '__main__':
    generator = SummaryGenerator(
        'datasets/llm-summary-testing/original', 'bard')
    generator.generate_summaries()

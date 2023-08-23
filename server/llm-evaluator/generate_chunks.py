from pathlib import Path
import asyncio
import concurrent.futures
import time

from server.components.summarizer.base_summarizer import Chunker
from server.utils.logger import logging
from server.utils.settings import settings

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    original_path = Path('datasets/llm-summary-testing/original')
    output_path = Path('datasets/llm-summary-testing/llama_chunks')
    files = list(original_path.iterdir())
    for file in files:
        chunks = Chunker().chunk_text(file.read_text(), safe_context_size=750)
        output_file_path = output_path / file.name
        output_file_path.write_text('\n'.join(chunks))

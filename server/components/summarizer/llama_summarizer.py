import asyncio

from llama_cpp import Llama

from server.components.summarizer.base_summarizer import BaseSummarizer
from server.utils.logger import logging
from server.utils.async_tools import make_async

logger = logging.getLogger(__name__)

CHUNK_SUMMARY_SYSTEM_MESSAGE = """
    You are a legal assistant who summarizes the provided court ruling.
    "You will receive:
    1. A summary of the court ruling's part that came immediately before (none if this is the beginning of the court ruling)
    2. The part of the court ruling that you should summarize
    Summarize what this part of the court ruling is about based on the text and what preceded it.
    Create your summary ONLY in Czech.
"""

CHUNK_SUMMARY_USER_MESSAGE = """
1. Previous summary: {previous}
2. Text to summarize: {text}
"""

RESULT_SUMMARY_SYSTEM_MESSAGE = """
    You are a legal assistant who creates a summary of a court ruling.
    You will receive several paragraphs summarizing parts of the ruling.
    Put these paragraphs together into a single coherent summary.
    Answer ONLY in Czech.
"""


class LlamaSummarizer(BaseSummarizer):
    llm_type = 'llama'
    MAX_CONTEXT_SIZE = 750

    def __init__(self, text: str, file_name: str = '') -> None:
        super().__init__(text=text, file_name=file_name, context_size=self.MAX_CONTEXT_SIZE)
        self.llm = Llama(
            model_path="/home/rehoumir/llama.cpp/models/7B/ggml-model-q4_0.bin", n_ctx=1200)

    @make_async
    def summarize_text_chunk(self, text_chunk: str):
        try:
            # TODO: improve prompt
            chat_completion = self.llm(
                f"Q: Shrň prosím toto soudní rozhodnutí:{text_chunk} A: ", max_tokens=250, stop=["Q:", "\n"], echo=True)

            # TODO:
            print(chat_completion)
            return chat_completion['choices'][0]['text']
        except Exception:
            logging.exception("Exception while calling llama.cpp:")

        return ""


if __name__ == '__main__':
    test_text = """
Návrhem, který se dostal do dispozice soudu dne [datum], se žalobce dožadoval vydání rozhodnutí, kterým by soud uložil žalovanému povinnost zaplatit žalobci částku ve výši 21 474 Kč, včetně zákonného úroku z prodlení z jím jednotlivě požadovaných částek, a v neposlední řadě se dožadoval přiznání práva na náhradu nákladů řízení, které účelně vynaložil k uplatnění svého práva proti žalovanému.
Žalobce se svého nároku po žalovaném dožaduje z titulu zákonného, kdy žalovaný si po určité období neplnil svojí zákonnou povinnost uloženou mu ustanovením § 1 odst. 2 z. č. 168/1999 Sb., neplnil si zákonné pojištění odpovědnosti z provozu vozidla. Žalobci tak vznikl nárok dožadovat se po žalovaném příspěvku nepojištěného vozidla za toto období.
"""
    summarizer = asyncio.run(LlamaSummarizer(
        test_text).summarize_text(cache_chunks=True))
    print(summarizer)

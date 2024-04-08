from robojudge.utils.logger import logger
from robojudge.utils.settings import SUMMARY_UNAVAILABLE_MESSAGE
from robojudge.utils.internal_types import Ruling
from robojudge.components.summarizer.langchain_summarizer import summarizer
from robojudge.components.summarizer.case_title_generator import title_generator


async def prepare_summary_and_title(case: Ruling):
    if not case.summary or case.summary == SUMMARY_UNAVAILABLE_MESSAGE:
        logger.info(f'Generating summary for text: "{case.reasoning[:200]}..."')
        summary = await summarizer.summarize(case.reasoning)
        case.summary = summary if summary else SUMMARY_UNAVAILABLE_MESSAGE
    if not case.title and case.summary != SUMMARY_UNAVAILABLE_MESSAGE:
        case.title = await title_generator.generate_title(case.summary)

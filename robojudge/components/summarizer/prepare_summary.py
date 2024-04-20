from robojudge.utils.logger import logger
from robojudge.utils.settings import SUMMARY_UNAVAILABLE_MESSAGE
from robojudge.utils.internal_types import Ruling
from robojudge.components.summarizer.langchain_summarizer import summarizer
from robojudge.components.summarizer.ruling_title_generator import title_generator


async def prepare_summary_and_title(ruling: Ruling):
    if not ruling.summary or ruling.summary == SUMMARY_UNAVAILABLE_MESSAGE:
        logger.info(f'Generating summary for ruling "{ruling.ruling_id}" and reasoning: "{ruling.reasoning[:200]}..."')
        summary = await summarizer.summarize(ruling.reasoning)
        ruling.summary = summary if summary else SUMMARY_UNAVAILABLE_MESSAGE
    if not ruling.title and ruling.summary != SUMMARY_UNAVAILABLE_MESSAGE:
        ruling.title = await title_generator.generate_title(ruling.summary)

from langchain_openai.chat_models import ChatOpenAI

from robojudge.utils.settings import settings
standard_llm = ChatOpenAI(
    openai_api_key=settings.OPENAI_API_KEY,
    openai_api_base=settings.OPENAI_API_BASE,
    model=settings.GPT_MODEL_NAME,
    temperature=0,
)

advanced_llm = ChatOpenAI(
    openai_api_key=settings.OPENAI_API_KEY,
    openai_api_base=settings.OPENAI_API_BASE,
    model=settings.AUTO_EVALUATOR_NAME,
    temperature=0,
)

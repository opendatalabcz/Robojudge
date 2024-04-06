from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


from robojudge.utils.logger import logger
from robojudge.components.reasoning.llm_definitions import standard_llm


class CaseTitleGenerator:
    NEXT_CHUNK_SIZE = 4096 - 1000

    SYSTEM_MESSAGE_TEMPLATE = """\
Your task is to create a short and interesting title for an article about a court ruling based on a summary of that ruling.
The title should relate to what the case was about. Avoid sounding like a tabloid.
Create your title ONLY in Czech.
Here is the summary: {summary}
"""

    def __init__(self) -> None:
        output_parser = StrOutputParser()
        prompt = PromptTemplate(
            template=self.SYSTEM_MESSAGE_TEMPLATE, input_variables=["summary"]
        )

        self.llm_chain = prompt | standard_llm | output_parser

    async def generate_title(self, summary: str) -> str:
        try:
            return await self.llm_chain.ainvoke(input={"summary": summary})
        except Exception:
            logger.exception("Error while generating title:")
            return ""


title_generator = CaseTitleGenerator()

if __name__ == "__main__":
    test_summary = """
Soud rozhodoval o žalobě, ve které žalobkyně požadovala zaplacení peněz od žalovaného za cestování bez platné jízdenky. Soud posoudil věc podle platného zákona o drahách, který umožňuje uložit cestujícímu, který nemá platný jízdní doklad, zaplacení jízdného a přirážky. V tomto případě byla přirážka stanovena na 1 500 Kč. Žalobkyně a žalovaný uzavřeli smlouvu o přepravě, podle které je žalovaný povinen zaplatit žalobkyni jízdné a přirážku. Žalobkyně má také právo na úrok z prodlení. Soud rozhodl, že žalobkyni náleží náhrada nákladů řízení ve výši 1 489 Kč, která zahrnuje soudní poplatek a odměnu advokáta.
"""

    async def main():
        print(await title_generator.generate_title(test_summary))

    import asyncio

    asyncio.run(main())

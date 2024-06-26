import asyncio
from async_lru import alru_cache

from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import RefineDocumentsChain, LLMChain

from robojudge.components.reasoning.llm_definitions import standard_llm
from robojudge.components.chunker import TextChunker
from robojudge.utils.settings import settings


SYSTEM_MESSAGE_TEMPLATE = """\
Your task is to answer a question about a court ruling.
You will receive parts of the ruling. Refine your answer ONLY if the new parts are relevant to the the question.
If you already found the answer, ignore new information.
If the question is obviously unrelated to something which could be discussed in a civil court ruling, reject to answer with an explanation why.
Create your answer ONLY in Czech.
"""


class RulingQuestionAnswerer:
    @classmethod
    @alru_cache
    async def answer_question(cls, question: str, text: str, llm_name=None) -> str:
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            f"Question: {question}"
            "Try to answer the question based on the initial court ruling part: {context}"
        )

        initial_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        document_variable_name = "context"
        initial_response_name = "prev_response"

        llm = standard_llm
        if llm_name:
            llm = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                model=llm_name,
                temperature=0,
            )

        initial_llm_chain = LLMChain(llm=llm, prompt=initial_prompt)

        prompt_refine = HumanMessagePromptTemplate.from_template(
            f"Question: {question}"
            "Here's your previous answer: {prev_response}. "
            "Refine your answer if need be by the following court ruling part:"
            "{context}"
        )
        refine_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, prompt_refine]
        )

        refine_llm_chain = LLMChain(llm=llm, prompt=refine_prompt)

        cls.refiner = RefineDocumentsChain(
            initial_llm_chain=initial_llm_chain,
            refine_llm_chain=refine_llm_chain,
            document_variable_name=document_variable_name,
            initial_response_name=initial_response_name,
        )

        chunks = TextChunker.split_text_into_llm_chunks(text)
        result, _ = await cls.refiner.acombine_docs(docs=chunks)
        return result


if __name__ == "__main__":
    test_reasoning = "Účastníci řízení na základě výzvy soudu souhlasili s\xa0tím, aby soud ve věci rozhodl bez nařízení jednání. Soud proto ve věci postupoval podle ustanovení § 115a o. s. ř., dle kterého k\xa0projednání věci samé není třeba nařizovat jednání, jestliže ve věci lze rozhodnout jen na základě účastníky předložených listinných důkazů a účastníci se práva účasti na projednávání věci vzdali, popřípadě s\xa0rozhodnutím ve věci bez nařízení jednání souhlasí.\nSoud dospěl k\xa0následujícímu skutkovému závěru. Žalovaný se přepravoval prostředkem veřejné dopravy provozovaným právním předchůdcem žalobkyně, a to dne [datum] na lince tramvaje [číslo]. Na výzvu kontrolora se neprokázal platnou jízdenkou, jízdné a přirážku k\xa0jízdnému nezaplatil. Výše jízdného 23\xa0Kč a přirážky k\xa0jízdnému 1\xa0500\xa0Kč jsou soudu známy z jeho úřední činnosti. Smlouvou o postoupení pohledávek ze dne [datum] právní předchůdce žalobkyně postoupil pohledávku žalobkyni.\nPodle § 37 odst. 4 písm. d) zák. č. 266/1994 Sb. průvodčí drážního vozidla, osoba, která řídí drážní vozidlo, nebo jiná osoba ve veřejné drážní osobní dopravě pověřená dopravcem a vybavená kontrolním odznakem nebo průkazem dopravce je oprávněna uložit cestujícímu, který se neprokázal platným jízdním dokladem, zaplacení jízdného a přirážky k\xa0jízdnému nebo vyžadovat od cestujícího osobní údaje potřebné k\xa0vymáhání jízdného a přirážky k\xa0jízdnému, pokud cestující nezaplatí na místě; osobními údaji potřebnými k\xa0vymáhání jízdného a přirážky k\xa0jízdnému se rozumí jméno, příjmení a datum a místo narození a adresa pro doručování.\nPodle § 37 odst. 5 písm. b) zák. č. 266/1994 Sb. je cestující povinen při nástupu do drážního vozidla, pobytu v\xa0něm a při výstupu z drážního vozidla na výzvu pověřené osoby se prokázat platným jízdním dokladem. Neprokáže-li se platným jízdním dokladem z příčin na své straně, je povinen zaplatit jízdné z nástupní do cílové stanice nebo, nelze-li bezpečně zjistit stanici, kde cestující nastoupil, z výchozí stanice vlaku a přirážku k\xa0jízdnému, nebo pokud nezaplatí cestující na místě, prokázat se osobním dokladem a sdělit osobní údaje potřebné k\xa0vymáhání jízdného a přirážky k\xa0jízdnému.\nPodle § 37 odst. 6 zák. č. 266/1994 Sb. výši přirážky stanoví dopravce v\xa0přepravních podmínkách. Výše přirážky nesmí přesáhnout částku 1\xa0500\xa0Kč. Přirážka za porušení podmínek stanovených přepravním řádem činí nejvýše 1\xa0000\xa0Kč.\nPodle § 7 odst. 6 vyhlášky č. 175/2000 Sb. nezakoupil-li si cestující jízdenku podle odstavce 3 nebo podle odstavce 5 a je přepravován bez platné jízdenky, považuje se za cestujícího, který se z příčin na své straně neprokázal platným jízdním dokladem.\nPodle § 1970 zákona č. 89/2012 Sb., občanského zákoníku, (dále jen„ o. z.”) po dlužníkovi, který je v\xa0prodlení se splácením peněžitého dluhu, může věřitel, který řádně splnil své smluvní a zákonné povinnosti, požadovat zaplacení úroku z prodlení, ledaže dlužník není za prodlení odpovědný. Výši úroku z prodlení stanoví vláda nařízením; neujednají-li strany výši úroku z prodlení, považuje se za ujednanou výše takto stanovená.\nProtože se žalovaný neprokázal platnou jízdenkou na výzvu pověřené osoby, a protože nezaplatil jízdné a přirážku k\xa0jízdnému, je nárok žalobkyně důvodný včetně požadavku na zákonný úrok z prodlení, požadovaného v\xa0souladu s\xa0prováděcím nařízením vlády č. 351/2013 Sb., přičemž pohledávka byla postoupena žalobkyni v\xa0souladu s\xa0§ 1879 a násl. o. z.\nO náhradě nákladů řízení rozhodl soud podle § 142 odst. 1 o. s. ř. tak, že přiznal žalobkyni, jež byla v\xa0řízení zcela úspěšná, nárok na náhradu nákladů řízení v\xa0částce 1\xa0489\xa0Kč Tyto náklady sestávají ze zaplaceného soudního poplatku v\xa0částce 400\xa0Kč a nákladů zastoupení advokátem, kterému náleží odměna stanovená dle § 6 odst. 1 a § 14b vyhlášky č. 177/1996 Sb., advokátního tarifu, (dále jen„ a. t.”) z tarifní hodnoty ve výši 1\xa0523\xa0Kč sestávající z částky 200\xa0Kč za každý ze tří úkonů právní služby realizovaných před podáním návrhu ve věci včetně tří paušálních náhrad výdajů po 100\xa0Kč dle § 14b odst. 5 písm. a) a. t. a daň z přidané hodnoty ve výši 21 % z částky 900\xa0Kč ve výši 189\xa0Kč."

    question = "Kterým dopravním prostředkem jel žalovaný?"

    res = asyncio.run(RulingQuestionAnswerer.answer_question(
        question, test_reasoning))
    print(res)

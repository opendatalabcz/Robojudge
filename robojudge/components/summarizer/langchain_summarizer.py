from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import Document
from langchain.chains import RefineDocumentsChain, LLMChain
import more_itertools

from robojudge.utils.logger import logging
from robojudge.utils.gpt_tokenizer import tokenizer
from robojudge.components.reasoning.llm_definitions import standard_llm

logger = logging.getLogger(__name__)

SYSTEM_MESSAGE_TEMPLATE = """\
Your task is to create an interesting summary of a court ruling.
You will receive the court ruling in parts and continuously refine your summary from the previous parts.
Ignore any mentions of litigation costs and fees, they are irrelevant
Create your summary ONLY in Czech and use a maximum of 7 sentences.
"""


class CaseSummarizer:
    NEXT_CHUNK_SIZE = 4096 - 1000

    def __init__(self) -> None:
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SYSTEM_MESSAGE_TEMPLATE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(
            "Summarize the initial part of the court ruling: {context}"
        )

        initial_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        document_variable_name = "context"
        initial_response_name = "prev_response"

        initial_llm_chain = LLMChain(llm=standard_llm, prompt=initial_prompt)

        prompt_refine = HumanMessagePromptTemplate.from_template(
            "Here's your previous summary: {prev_response}. "
            "Update the summary based on the following part."
            "Ignore any mentions of litigation costs and fees, they are irrelevant"
            "Create your summary ONLY in Czech and use a maximum of 7 sentences."
            "{context}"
        )
        refine_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, prompt_refine]
        )

        refine_llm_chain = LLMChain(llm=standard_llm, prompt=refine_prompt)

        self.refiner = RefineDocumentsChain(
            initial_llm_chain=initial_llm_chain,
            refine_llm_chain=refine_llm_chain,
            document_variable_name=document_variable_name,
            initial_response_name=initial_response_name,
        )

    async def summarize(self, text: str) -> str:
        try:
            chunks = CaseSummarizer.split_text_into_chunks(text)
            result, summary_metadata = await self.refiner.acombine_docs(chunks)
            return result
        except Exception:
            logger.exception(f'Error while summarizing text:')
            return ''

    @classmethod
    def split_text_into_chunks(cls, text: str):
        chunks = []

        tokens = tokenizer.encode(text)
        if len(tokens) <= cls.NEXT_CHUNK_SIZE:
            chunks.append(Document(page_content=text))
        else:
            split_tokens = more_itertools.chunked(tokens, cls.NEXT_CHUNK_SIZE)
            chunks.extend(
                [
                    Document(page_content=tokenizer.decode(token_batch))
                    for token_batch in split_tokens
                ]
            )

        return chunks


summarizer = CaseSummarizer()

if __name__ == "__main__":
    test_text = """
1. Žalobce se žalobou doručenou Městskému soudu v Brně dne 23. 4. 2021 domáhal vydání rozhodnutí, kterým by soud stanovil žalovanému povinnost zaplatit žalobci částku ve výši
15.000 Kč s kapitalizovaným úrokem z prodlení ve výši 1.767,12 Kč a s úrokem z prodlení ve výši 10 % ročně z této částky od 22. 12. 2020 do zaplacení, a dále částku ve výši 7.300 Kč
a částku ve výši 6.450 Kč.
2. Žalobu odůvodnil tím, že dne 26. 7. 2018 byla mezi právním předchůdcem žalobce (společností [právnická osoba]) a žalovaným uzavřena Smlouva o úvěru [číslo] na základě níž byly žalovanému poskytnuty finanční prostředky ve výši 15.000 Kč. Žalovaný se zavázal vrátit právnímu předchůdci žalobce úvěr ve výši 15.000 Kč a dále uhradit částku v celkové výši
12.900 Kč (sestávající z kapitalizovaného úroku, z poplatku za správu úvěru a z poplatku za hotovostní inkaso splátek) prostřednictvím 14 měsíčních splátek ve výši 1.992,86 Kč, přičemž poslední splátka byla splatná dne 26. 9. 2019. Žalovaný však nehradil sjednané splátky řádně
a včas, kdy uhradil pouze částku v celkové výši 5.600 Kč. Žalobou uplatněná pohledávka sestává z dlužné jistiny ve výši 15.000 Kč, z dlužného úroku ve výši 2.175 Kč, z dlužného poplatku za správu úvěru ve výši 1.825 Kč a z dlužného poplatku za hotovostní výběr splátek ve výši
3.300 Kč. Žalobce se dále po žalovaném domáhá i zaplacení kapitalizovaného úroku z prodlení ve výši 1.767,12 Kč (tj. úroku z prodlení z částky [číslo] K od 27. 9. 2019 do 30. 11. 2020)
a zaplacení smluvní pokuty ve výši 0,1 % denně z částky 15.000 Kč, kterou za období od
27. 9. 2019 do 30. 11. 2020 kapitalizoval částkou ve výši 6.450 Kč. Na základě Smlouvy
o postoupení pohledávek ze dne 21. 12. 2020 byla na žalobce postoupena mimo jiné i pohledávka za žalovaným.
3. Žalovaný se k nároku uplatněnému žalobou nevyjádřil.
4. Soud k projednání věci nařídil na den 16. 5. 2022 jednání, k němuž se žalovaný bez důvodné
a včasné omluvy nedostavil, žalobce se z jednání omluvil v podání doručeném soudu dne
25. 4. 2022.
5. V projednávané věci provedl soud dokazování listinnými důkazy, z nichž zjistil následující skutečnosti. Dne 26. 7. 2018 byla mezi právním předchůdcem žalobce (společností [právnická osoba]) a žalovaným uzavřena Smlouva o úvěru [číslo] na základě které poskytl právní předchůdce žalobce žalovanému v hotovosti úvěr ve výši 15.000 Kč a žalovaný se zavázal vrátit právnímu předchůdci žalobce úvěr ve výši 15.000 Kč a dále uhradit částku ve výši 12.900 Kč (celkové náklady spotřebitelského úvěru), tj. zaplatit částku v celkové výši 27.900 Kč,
a to prostřednictvím 14 měsíčních splátek ve výši 1.950 Kč dle předpisu splátek. Žalovaný současně podepsal i Předpis splátek a Formulář pro standardní informace o spotřebitelském úvěru. O úvěr požádal žalovaný dne 26. 7. 2018, v žádosti bylo uvedeno, že žalovaný je zaměstnán na dobu určitou do 31. 12. 2018, jeho celkové měsíční příjmy činí 8.498 Kč a jeho celkové měsíční výdaje činí 4.500 Kč (Žádost o poskytnutí spotřebitelského úvěru ze dne 26. 7. 2018, Smlouva o úvěru [číslo] ze dne 26. 7. 2018, Předpis splátek ke smlouvě o úvěru [číslo] ze dne 26. 7. 2018, Formulář pro standardní informace o spotřebitelském úvěru ze dne 26. 7. 2018). Žalovaný uhradil právnímu předchůdci žalobce částku v celkové výši 5.600 Kč (Listina označená jako [anonymizováno] [číslo]). Dne 6. 9. 2018 byla mezi společností [právnická osoba] jakožto prodávajícím
a společností [právnická osoba] jakožto kupujícím uzavřena Smlouva o prodeji části závodu, který je tvořen divizí spotřebitelských úvěrů a dne 21. 12. 2020 byla mezi společností [právnická osoba] jakožto postupitelem a žalobcem jakožto postupníkem uzavřena Smlouva
o postoupení pohledávek, na základě níž byla na žalobce postoupena mimo jiné i pohledávka za žalovaným, což bylo žalovanému oznámeno dopisem postupitele ze dne 19. 1. 2021, předaným dne 22. 1. 2021 k poštovní přepravě (Notářský zápis NZ [číslo], [spisová značka] sepsaný dne
27. 9. 2018 notářkou JUDr. [jméno] [příjmení], Smlouva o postoupení pohledávek ze dne 21. 12. 2020, Oznámení o postoupení pohledávky ze dne 19. 1. 2021). Žalovaný byl dopisem zástupce žalobce ze dne 15. 3. 2021, který byl dne 17. 3. 2021 předán k poštovní přepravě, vyzván k úhradě částky v celkové výši 33.711,94 Kč (Výzva před podáním žaloby ze dne 15. 3. 2021).
6. Ohledně skutkového stavu tak lze uzavřít, že na základě Smlouvy o úvěru [číslo] uzavřené dne 26. 7. 2018 byl žalovanému poskytnut úvěr ve výši 15.000 Kč, který se žalovaný zavázal splácet včetně celkových nákladů spotřebitelského úvěru ve výši 12.900 Kč, prostřednictvím 14 měsíčních splátek ve výši 1.950 Kč. Žalovaný uhradil právnímu předchůdci žalobce částku v celkové výši 5.600 Kč.
7. Podle ustanovení § 2395 zákona č. 89/2012 Sb., občanský zákoník (dále jen jako „občanský zákoník“) smlouvou o úvěru se úvěrující zavazuje, že úvěrovanému poskytne na jeho požádání
a v jeho prospěch peněžní prostředky do určité částky, a úvěrovaný se zavazuje poskytnuté peněžní prostředky vrátit a zaplatit úroky.
8. Podle ustanovení § 86 odst. 1 zákona č. 257/2016 Sb., o spotřebitelském úvěru (dále jen jako „zákon o spotřebitelském úvěru“) poskytovatel před uzavřením smlouvy o spotřebitelském úvěru nebo změnou závazku z takové smlouvy spočívající ve významném navýšení celkové výše spotřebitelského úvěru posoudí úvěruschopnost spotřebitele na základě nezbytných, spolehlivých, dostatečných a přiměřených informací získaných od spotřebitele, a pokud je to nezbytné, z databáze umožňující posouzení úvěruschopnosti spotřebitele nebo i z jiných zdrojů. Poskytovatel poskytne spotřebitelský úvěr jen tehdy, pokud z výsledku posouzení úvěruschopnosti spotřebitele vyplývá, že nejsou důvodné pochybnosti o schopnosti spotřebitele spotřebitelský úvěr splácet.
9. Podle ustanovení § 87 odst. 1 zákona o spotřebitelském úvěru poskytne-li poskytovatel spotřebiteli spotřebitelský úvěr v rozporu s § 86 odst. 1 větou druhou, je smlouva neplatná. Spotřebitel může uplatnit námitku neplatnosti v tříleté promlčecí lhůtě běžící ode dne uzavření smlouvy. Spotřebitel je povinen vrátit poskytnutou jistinu spotřebitelského úvěru v době přiměřené jeho možnostem.
10. Podle ustanovení § 580 odst. 1 občanského zákoníku neplatné je právní jednání, které se příčí dobrým mravům, jakož i právní jednání, které odporuje zákonu, pokud to smysl a účel zákona vyžaduje.
11. Podle ustanovení § 588 občanského zákoníku soud přihlédne i bez návrhu k neplatnosti právního jednání, které se zjevně příčí dobrým mravům, anebo které odporuje zákonu a zjevně narušuje veřejný pořádek. To platí i v případě, že právní jednání zavazuje k plnění od počátku nemožnému.
12. Podle ustanovení § 1813 občanského zákoníku má se za to, že zakázaná jsou ujednání, která zakládají v rozporu s požadavkem přiměřenosti významnou nerovnováhu práv nebo povinností stran v neprospěch spotřebitele. To neplatí pro ujednání o předmětu plnění nebo ceně, pokud jsou spotřebiteli poskytnuty jasným a srozumitelným způsobem.
13. Podle ustanovení § 2991 občanského zákoníku kdo se na úkor jiného bez spravedlivého důvodu obohatí, musí ochuzenému vydat, oč se obohatil (odst. 1). Bezdůvodně se obohatí zvláště ten, kdo získá majetkový prospěch plněním bez právního důvodu, plněním z právního důvodu, který odpadl, protiprávním užitím cizí hodnoty nebo tím, že za něho bylo plněno, co měl po právu plnit sám (odst. 2).
14. Na základě zjištěného skutkového stavu a po jeho právním posouzení dospěl soud k závěru, že žaloba je důvodná pouze částečně.
15. V řízení bylo prokázáno, že dne 26. 7. 2018 byla mezi právním předchůdcem žalobce
a žalovaným uzavřena Smlouva o úvěru [číslo] (dále jen jako„ Smlouva“) ve smyslu ustanovení § 2395 a násl. občanského zákoníku. Na základě této Smlouvy poskytl právní předchůdce žalobce žalovanému dne 26. 7. 2018 peněžní prostředky ve výši 15.000 Kč. Právní předchůdce žalobce uzavřel Smlouvu jakožto podnikatel, žalovaný poté jakožto spotřebitel. Soud se tedy nejprve z úřední povinnosti (SDEU C -679/18 OPR-Finance) zabýval tím, zda právní předchůdce žalobce před uzavřením Smlouvy posoudil schopnost žalovaného úvěr splácet s odbornou péčí, tak jak mu ukládá ustanovení § 86 odst. 1 zákona o spotřebitelském úvěru
(k tomu srov. nález Ústavního soudu sp. zn. III. ÚS 4129/18 ze dne 26. 2. 2019), přičemž součástí odborné péče věřitele je taková obezřetnost, že poskytovatel úvěru nespoléhá na údaje
o schopnosti splácet tvrzené samotným dlužníkem, ale sám tyto údaje prověří, případně si je nechá od dlužníka doložit (k tomu srov. rozsudek Nejvyššího správního soudu sp. zn. 1 As 30/2015 ze dne 1. 4. 2015). Takto rozsáhlé požadavky na prověřování poměrů dlužníka ze strany věřitele jsou dány vývojem spotřebitelských vztahů, který má negativní celospolečenské dopady
a vede ke spirále předlužování spotřebitelů, včetně pádu spotřebitele a všech osob na něm závislých do veřejné sociální sítě, narušení rodinných a sociálních vztahů, jejich přechodu do šedé ekonomiky atd. (k tomu srov. rozsudek Nejvyššího soudu ČR sp. zn. 33 Cdo 2178/2018 ze dne
25. 7. 2018). Z předložených listinných důkazů však nevyplývá, že by právní předchůdce žalobce reálně nějak, natož pak s odbornou péčí, schopnost žalovaného úvěr splácet posoudil, kdy tvrzení žalobce obsažená v návrhu na zahájení řízení o vyhodnocení informací požadovaných a získaných od žalovaného a o jejich ověřování nejsou žádným způsobem doložena. Za této situace tak nelze dospět k jinému závěru, než že právní předchůdce žalobce jakožto poskytovatel úvěru své povinnosti posoudit schopnost žalovaného splácet úvěr s odbornou péčí nedostál a pokud této povinnosti nedostál, je Smlouva s odkazem na ustanovení § 87 odst. 1 zákona o spotřebitelském úvěru a na ustanovení § 588 občanského zákoníku pro rozpor se zákonem absolutně neplatná, neboť jde o smlouvu, která svým účelem odporuje zákonu (k tomu srov. opět rozsudek Nejvyššího soudu ČR sp. zn. 33 Cdo 2178/2018 ze dne 25. 7. 2018 či opět nález Ústavního soudu sp. zn. III. ÚS 4129/18 ze dne 26. 2. 2019).
16. Nad rámec výše uvedeného soud doplňuje i další důvod neplatnosti Smlouvy, a to zjevný rozpor jejího obsahu s dobrými mravy (ustanovení § 588 občanského zákoníku) a skutečnost, že v rozporu s požadavkem přiměřenosti stanoví významnou nerovnováhu práv
a povinností v neprospěch žalovaného jako spotřebitele (ustanovení § 1813 občanského zákoníku), kdy tomto směru nelze přehlédnout naprostý nepoměr mezi výši částky poskytnuté právním předchůdcem žalobce (tj. 15.000 Kč) a výši částky, které se právnímu předchůdci žalobce za poskytnutí úvěru mělo dostat (tj. 27.900 Kč) během relativně krátké doby (tj.
14 měsíců).
17. Absolutní neplatnost právního jednání přitom působí přímo (automaticky) ze zákona (ex lege),
a to od počátku (ex tunc), proto subjektivní práva a povinnosti z takto absolutně neplatného právního jednání nevzniknou a absolutně neplatné právní jednání nemůže vyvolat smluvními stranami předvídané důsledky. Právnímu předchůdci žalobce tak právo na zaplacení požadovaného smluvního úroku, požadovaného smluvního poplatku a požadované smluvní pokuty nevzniklo a nelze je proto žalobci přiznat. Pokud však žalovaný na základě této neplatné Smlouvy její předmět převzal (tj. čerpal po 26. 7. 2018 ve svůj prospěch peněžní prostředky ve výši 15.000 Kč), je povinen takto vyčerpané peněžní prostředky vrátit žalobci jakožto bezdůvodné obohacení (ustanovení § 2991 a násl. občanského zákoníku). Pokud bylo v tomto směru prokázáno, že žalovaný uhradil právnímu předchůdci žalobce toliko částku ve výši
5.600 Kč, je žalobou uplatněný nárok důvodný co do rozdílu mezi částkou čerpanou
(tj. 15.000 Kč) a částkou již vrácenou (tj. 5.600 Kč). S ohledem na právě uvedené tedy soud žalobě v této části vyhověl a ve výroku I. tohoto rozsudku zavázal žalovaného k povinnosti zaplatit žalobci částku ve výši 9.400 Kč. Jelikož žalovaný nesplnil svou povinnost týkající se uplatněného práva včas, dostal se do prodlení a je tak v souladu s ustanovením § 1970 občanského zákoníku povinen zaplatit z těchto částek i úrok z prodlení. Vzhledem k tomu, že doba plnění pro nárok na vydání bezdůvodného obohacení není stanovena zákonem
a v posuzovaném případě nebyla ani účastníky dohodnuta, stává se závazek z bezdůvodného obohacení splatným bez zbytečného odkladu po výzvě věřitele dle ustanovení § 1958 odst. 2 občanského zákoníku (k tomu srov. např. rozsudek Nejvyššího soudu ČR sp. zn. 30 Cdo 5464/2016 ze dne 24. 10. 2018). Za výzvu k vydání bezdůvodného obohacení lze v tomto směru považovat dopis zástupce žalobce ze dne 15. 3. 2021, který byl dne 17. 3. 2021 předán k poštovní přepravě a žalovanému došel v souladu se zákonnou domněnkou dojití (ustanovení § 573 občanského zákoníku) třetí pracovní den, tj. v pondělí 22. 3. 2021 a za dobu bez zbytečného odkladu lze tedy považovat čtvrtek 25. 3. 2021. Nárok na vydání bezdůvodného obohacení se tak teprve dne 25. 3. 2021 stal splatným a soud přiznal žalobci až ode dne následujícího, tj. od
26. 3. 2021, úrok z prodlení ve výši stanovené nařízením č. 351/2013 Sb. Ve zbývajícím rozsahu, tj. ohledně zaplacení částky ve výši 5.600 Kč (jistina), částky ve výši 7.300 Kč (úrok + poplatky), částky ve výši 6.450 Kč (smluvní pokuta) a ohledně zaplacení kapitalizovaného úroku z prodlení
a ohledně zaplacení úroku z prodlení za dobu delší a ve výši neodpovídající zákonnému úroku z prodlení, soud žalobu ve výroku II. tohoto rozsudku zamítnul.
18. Sluší se v této souvislosti poznamenat, že při nařízení jednání bylo žalobci výslovně sděleno, že jeho účast při jednání je nutná. Toto sdělení bylo žalobci adresováno právě z důvodu nedostatečných skutkových tvrzení tak, aby mohl být při nařízeném jednání vyzván k doplnění skutkových tvrzení a k označení důkazů podle ustanovení §118a odst. 1 a 3 občanského soudního řádu (dále jen jako „o.s.ř.“). Pokud jde o poučovací povinnost soudu ve smyslu tohoto ustanovení o.s.ř., jedná se o poučovací povinnost soudu při jednání. Znamená to, že účastník, který se nedostavil k jednání, znemožnil soudu, aby mu poskytl poučení podle ustanovení § 118a o.s.ř. Nemohl-li soud poskytnout účastníku poučení podle ustanovení § 118a o.s.ř. proto, že se nedostavil k jednání, není oprávněn a povinen mu sdělovat potřebná poučení jinak a není ani povinen jen z tohoto důvodu odročovat jednání (k tomu srov. Drápal, L., Bureš, J. a kol. Občanský soudní řád I. §1 až 200za. Komentář. I. vydání. Praha: C. H. Beck, 2009 s. 831). V projednávané věci se žalobce k nařízenému jednání nedostavil, a proto ho soud nemohl poučit o povinnosti tvrdit rozhodující skutečnosti a označit k těmto skutkovým tvrzením důkazy. Svojí nepřítomností při jednání zbavil žalobce soud možnosti poskytnout mu potřebné poučení ke splnění jeho povinnosti stran žalobou uplatněného nároku (k tomu srov. rozsudek Nejvyššího soudu ČR sp. zn. 30 Cdo 3970/2008 ze dne 20. 5. 2010), když nedostaví-li se k jednání řádně předvolaný účastník
a v důsledku této skutečnosti mu nelze poskytnout poučení dle ustanovení § 118a odst. 3 o.s.ř., nahlíží se na něj jako na účastníka řádně poučeného (k tomu srov. usnesení Nejvyššího soudu ČR sp. zn. 28 Cdo 1537/2008 ze dne 29. 4. 2008). Soud tak v souladu s ustanovením § 101 odst. 3 o.s.ř. vycházel z obsahu spisu a z provedených důkazů. Opačný postup soudu (odročení jednání pouze za účelem vyzvání žalobce k doplnění skutkových tvrzení a označení důkazů) by bylo porušením zásady rovnosti účastníků řízení (ustanovení § 18 odst. 1 věta první o.s.ř.)
19. Výrok III. o náhradě nákladů řízení je odůvodněn ustanovením § 142 odst. 2 o.s.ř. podle něhož měl-li účastník ve věci úspěch jen částečný, soud náhradu nákladů poměrně rozdělí, popřípadě vysloví, že žádný z účastníků nemá na náhradu nákladů právo. Sluší se v této souvislosti poznamenat, že soud při rozhodování o náhradě nákladů řízení dle míry úspěchu zvážil míru úspěchu v celém sporu, tj. nejen ohledně samotné pohledávky, ale též stran jejího příslušenství
(k tomu srov. nález Ústavního soudu sp. zn. I. ÚS 2717/08 ze dne 30. 8. 2010), a že pro zjednodušení výpočtu úspěchu účastníků stanovil pro výpočet nároků požadovaných do zaplacení limit 16. 5. 2022, tj. den vydání tohoto rozsudku. Předmětem řízení bylo zaplacení částky v celkové výši 32.617,11 Kč (15.000 Kč + 2.100 Kč + 1.767,11 Kč + 7.300 Kč + 6.450 Kč). Úspěch žalobce je v tomto případě představován výrokem I. tohoto rozsudku, tedy částkou v celkové výši 10.285,98 Kč (9.400 Kč + 885,98 Kč), ohledně které soud žalobě vyhověl. Naopak úspěch žalovaného je představován výrokem II. tohoto rozsudku, tedy částkou v celkové výši 22.331,13 Kč (5.600 Kč + 386,30 Kč + 639,78 Kč + 187,93 Kč + 1.767,12 Kč + 7.300 Kč + 6.450 Kč), ohledně které byla žaloba zamítnuta. Žalobce byl proto úspěšný v 31,5 % předmětu řízení, žalovaný byl úspěšný v 68,5 % a po vzájemném zápočtu úspěchu žalovaného vůči úspěchu žalobce, by žalovaný měl právo na náhradu 37 % účelně vynaložených nákladů. Vzhledem k tomu však, že žalovanému v tomto směru žádné náklady řízení nevznikly, rozhodl soud tak, jak je ve výroku III. tohoto rozsudku uvedeno.
"""
    print(summarizer.summarize(test_text))

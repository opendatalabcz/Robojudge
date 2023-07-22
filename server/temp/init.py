import asyncio

from server.db.chroma_db import embedding_db
from server.db.mongo_db import metadata_db
from server.tasks.fetch_new_cases import fetch_new_cases
from server.scraper.case_page_scraper import CasePageScraper

from server.model.lemmatizer import lemmatizer

# https://rozhodnuti.justice.cz/rozhodnuti/435673

test_text = """
Návrhem, který se dostal do dispozice soudu dne [datum], se žalobce dožadoval vydání rozhodnutí, kterým by soud uložil žalovanému povinnost zaplatit žalobci částku ve výši 21 474 Kč, včetně zákonného úroku z prodlení z jím jednotlivě požadovaných částek, a v neposlední řadě se dožadoval přiznání práva na náhradu nákladů řízení, které účelně vynaložil k uplatnění svého práva proti žalovanému.
Žalobce se svého nároku po žalovaném dožaduje z titulu zákonného, kdy žalovaný si po určité období neplnil svojí zákonnou povinnost uloženou mu ustanovením § 1 odst. 2 z. č. 168/1999 Sb., neplnil si zákonné pojištění odpovědnosti z provozu vozidla. Žalobci tak vznikl nárok dožadovat se po žalovaném příspěvku nepojištěného vozidla za toto období.
Okresní soud v Domažlicích v dané věci měl splněny předpoklady pro přistoupení k rozhodnutí bez nařízení ústního jednání postupem podle § 115a o. s. ř.
Soud má za prokázaná následující skutková zjištění.
Žalovaný jako vlastník a provozovatel osobního automobilu SPZ 4 [číslo] [číslo] si neplnil po období od [datum] do 7.5. 219 - 6 dní pojištění odpovědnosti z provozu vozidla, přestože mu tuto povinnost ukládá ustanovení § 1 odst. 2 zákona č. 168/1999 Sb. Žalobci tak vznikl nárok dožadovat se po žalovaném příspěvku nepojištěného vozidla s poukazem na § 4 odst. 1 zákona č. 168/1999 Sb. ve spojení s § 2 odst. 1 písm. I) vyhlášky č. 205/1999 Sb. pro den 93Kč x 6 dní, celkem 558 Kč.
V souvislosti s mimosoudním uplatněním nároku vznikl žalobci nárok dožadovat se po žalovaném s poukazem na § 4 odst. 4 zákona č. 168/1999 Sb. ve spojení s § 2a vyhlášky č. 205/1999 Sb. poplatku ve výši 300 Kč. Žalovaný byl ze strany žalobce upozorněn a vyzván k dobrovolné úhradě, ve lhůtě žalobcem určené však jím požadovanou úhradu nerealizoval.
Žalovaný jako vlastník a provozovatel osobního automobilu SPZ 4 [číslo] [číslo] si neplnil po období od [datum] do [datum] -76 dní pojištění odpovědnosti z provozu vozidla, přestože mu tuto povinnost ukládá ustanovení § 1 odst. 2 zákona č. 168/1999 Sb. Žalobci tak vznikl nárok dožadovat se po žalovaném příspěvku nepojištěného vozidla s poukazem na § 4 odst. 1 zákona č. 168/1999 Sb. ve spojení s § 2 odst. 1 písm. I) vyhlášky č. 205/1999 Sb. pro den 93Kč x 76 dní, celkem 7068 Kč.
V souvislosti s mimosoudním uplatněním nároku vznikl žalobci nárok dožadovat se po žalovaném s poukazem na § 4 odst. 4 zákona č. 168/1999 Sb. ve spojení s § 2a vyhlášky č. 205/1999 Sb. poplatku ve výši 300 Kč. Žalovaný byl ze strany žalobce upozorněn a vyzván k dobrovolné úhradě, ve lhůtě žalobcem určené však jím požadovanou úhradu nerealizoval.
Žalovaný jako vlastník a provozovatel osobního automobilu [registrační značka] si neplnil po období od [datum] do [datum] dní pojištění odpovědnosti z provozu vozidla, přestože mu tuto povinnost ukládá ustanovení § 1 odst. 2 zákona č. 168/1999 Sb. Žalobci tak vznikl nárok dožadovat se po žalovaném příspěvku nepojištěného vozidla s poukazem na § 4 odst. 1 zákona č. 168/1999 Sb. ve spojení s § 2 odst. 1 písm. I) vyhlášky č. 205/1999 Sb. pro den 93Kč x 65 dní, celkem 6045 Kč.
V souvislosti s mimosoudním uplatněním nároku vznikl žalobci nárok dožadovat se po žalovaném s poukazem na § 4 odst. 4 zákona č. 168/1999 Sb. ve spojení s § 2a vyhlášky č. 205/1999 Sb. poplatku ve výši 300 Kč. Žalovaný byl ze strany žalobce upozorněn a vyzván k dobrovolné úhradě, ve lhůtě žalobcem určené však jím požadovanou úhradu nerealizoval.
Žalovaný jako vlastník a provozovatel osobního automobilu [registrační značka] si neplnil po období od [datum] do [datum] – 71 dní pojištění odpovědnosti z provozu vozidla, přestože mu tuto povinnost ukládá ustanovení § 1 odst. 2 zákona č. 168/1999 Sb. Žalobci tak vznikl nárok dožadovat se po žalovaném příspěvku nepojištěného vozidla s poukazem na § 4 odst. 1 zákona č. 168/1999 Sb. ve spojení s § 2 odst. 1 písm. I) vyhlášky č. 205/1999 Sb. pro den 93Kč x 71 dní, celkem 6603 Kč.
V souvislosti s mimosoudním uplatněním nároku vznikl žalobci nárok dožadovat se po žalovaném s poukazem na § 4 odst. 4 zákona č. 168/1999 Sb. ve spojení s § 2a vyhlášky č. 205/1999 Sb. poplatku ve výši 300 Kč. Žalovaný byl ze strany žalobce upozorněn a vyzván k dobrovolné úhradě, ve lhůtě žalobcem určené však jím požadovanou úhradu nerealizoval.
Vzhledem k tomu, že žalovaný se dostal se splněním svých povinností vůči žalobci do prodlení, nárokuje žalobce po žalovaném zcela po právu i zákonný úrok z prodlení z jím požadované částky postupem podle § 1970 z. č. 89/2012 Sb.
Rozhodnutí o náhradě nákladů řízení má pak oporu v § 142 odst. 1 o. s. ř. V daném případě to byl žalobce, kdo byl plně ve věci úspěšný, a komu náleží právo na přiznání plné náhrady nákladů řízení, které účelně vynaložil k uplatnění svého práva proti žalovanému. Předmětné náklady představuje zaplacený soudní poplatek ve výši 1074 Kč, odměna za 3 úkony právní služby – 3 x 300 Kč podle § 14b odst. 1 vyhl. 177/1996 Sb., 3 režijní paušály – 3 x 100 Kč podle § 14b odst. 5 vyhl. 177/1996 Sb., 21% DPH ze součtu odměny a režijních paušálů. Celkem tak byla žalovanému uložena povinnost zaplatit žalobci na náhradě nákladů řízení částka ve výši 2526 Kč, kterou je žalovaný povinen uhradit s poukazem na ustanovení § 149 odst. 1 o. s. ř. k rukám advokátky Mgr. [jméno] [příjmení].
"""

async def main():
    # case = await CasePageScraper(435673).scrape_case()

    lemmatized = await lemmatizer.lemmatize_text(test_text)
    print(lemmatized)

    # embedding_db.upsert_cases([case])
    # metadata_db.upsert_metadata([case])

    # await fetch_new_cases()

if __name__ == '__main__':
    asyncio.run(main())

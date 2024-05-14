# Robojudge
Tento repozitář obsahuje webovou aplikaci, která využívá Large Language Modely (LLM) k analýze získaných soudních rozsudků a zobrazuje výsledky prostřednictvím webového rozhraní.

Aplikace se skládá z FE, BE, dokumentové a vektorové databáze a stahovače (scraperu) rozhodnutí. Pro fungování jsou potřeba všechny tyto komponenty. Podrobnosti jsou uvedeny v související bakalářské práci a v kódu samotném.
![robojudge_arch_new](https://github.com/opendatalabcz/Robojudge/assets/42498748/3ec115aa-4efa-43f8-bdbe-729507589656)


## Instalace
Repozitář obsahuje soubor `docker-compose.yaml`, který umožňuje spustit všechny potřebné aplikace jako kontejnery.

1. Vytvořte soubor `.env` z přiloženého `.env.example` a vyplňte potřebné hodnoty. Většina defaultních nastavení by měla fungovat, avšak hodnoty OpenAI klíčů (samozřejmě) předvyplněné nejsou.
- Klíčové je dodat především hodnoty týkající se `OPENAI*`.
2. Spusťte aplikace pomocí `docker compose up`.

## API dokumentace
Dokumentace API je dostupná při lokálním spuštění na endpointu `/docs` nebo v nasazené aplikaci zde: https://robojudge.opendatalab.cz/docs.

## Stahovač rozhodnutí
Stahovač je řízen pomocí knihovny Dramatiq, která spouští několik procesů 2 druhů: fetcher stahuje rozhodnutí z webu justice.cz a parser nechává generovat embeddingy na serverech OpenAI a následně je ukládá do databází. Celý proces stahování je znázorněn níže:
![scraper_new_arch](https://github.com/opendatalabcz/Robojudge/assets/42498748/7a560c88-d51e-4134-8625-77a482b36343)

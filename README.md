# Robojudge
Tento repozitář obsahuje webovou aplikaci, která využívá Large Language Modely (LLM) k analýze získaných soudních rozsudků a zobrazuje výsledky prostřednictvím webového rozhraní. 

## Instalace
Repozitář obsahuje soubor `docker-compose.yaml`, který umožňuje spustit všechny potřebné aplikace jako kontejnery.

1. Vytvořte soubor `.env` z přiloženého `.env.example` a vyplňte potřebné hodnoty. Většina defaultních nastavení by měla fungovat, avšak hodnoty OpenAI klíčů (samozřejmě) předvyplněné nejsou.
- Klíčové je dodat především hodnoty týkající se `OPENAI*`.
2. Spusťte aplikace pomocí `docker compose up`.
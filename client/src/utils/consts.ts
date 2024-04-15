export const DEFAULT_HELPER_TEXT = `Zadejte popis nebo text případu, pro který chcete najít již rozhodnuté podobné
                  případy. Databáze momentálně obsahuje hlavně rozhodnutí civilních soudů v 1. stupni (viz "INFO").`;

export const MIN_DESCRIPTION_LENGTH = 20;
export const MAX_DESCRIPTION_LENGTH = 20000;
export const MAX_QUESTION_LENGTH = 250;

export const INPUT_TOO_SHORT = `Zadejte prosím delší popis případu (aspoň ${MIN_DESCRIPTION_LENGTH} znaků).`;
export const INPUT_TOO_LONG = `Zadejte prosím maximálně ${MAX_DESCRIPTION_LENGTH} znaků.`;
export const QUESTION_INPUT_TOO_LONG = `Zadejte prosím maximálně ${MAX_QUESTION_LENGTH} znaků.`;

export const EMPTY_FILTER_ALERT =
  "Nebyla nalezena žádná rozhodnutí splňující parametry vyhledávání. Zkuste změnit vyhledávaná období.";

export const SERVER_URL =
  process.env.REACT_APP_SERVER_URL ?? "http://localhost:4000";

export const queryExamples = [
  {
    text: "Soud řešil rozvod manželství, protože každý z manželů měl jiného partnera a nechtěli spolu zůstat.",
  },
  { text: "Muž cestoval v MHD a dostal pokutu, protože jel načerno. Žalobce pokutu vymáhá u soudu." },
];

export const TOO_MANY_QUERIES_ALERT =
  "Zaslali jste příliš mnoho dotazů v krátkém čase. Opakujte prosím akci za chvíli.";

export const FETCH_SUMMARIES_ERROR_ALERT =
  "Při vytváření shrnutí nastala chyba. Opakujte prosím akci za chvíli.";

export const FETCH_ANSWER_ERROR_ALERT =
  "Při dotazování nastala chyba. Opakujte prosím akci za chvíli.";

export const CLICK_TO_COPY_PROMPT = "Kliknutím zkopírujete číslo jednací.";

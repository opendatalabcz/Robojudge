from sentence_transformers import SentenceTransformer

from transformers import AutoModel
import torch
import torch.nn.functional as F

from robojudge.utils.settings import settings
from research.tokenizer import retrieve_tokenizer


class Embeddder:
    model: SentenceTransformer

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            model_name_or_path=settings.EMBEDDING_MODEL, cache_folder=settings.EMBEDDING_CACHE_DIR)

    def embed_texts(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True).tolist()
        # return self.model.encode(texts, convert_to_tensor='pt')

    def score(self, texts: list[str], query: str, custom_encode=True):
        # Encode query and docs
        query_emb = self.embed_texts_with_custom_tokenizer(
            [query]) if custom_encode else self.embed_texts([query])
        doc_emb = self.embed_texts_with_custom_tokenizer(
            texts)if custom_encode else self.embed_texts(texts)

        # Compute dot score between query and all document embeddings
        scores = torch.mm(query_emb, doc_emb.transpose(0, 1))[0].cpu().tolist()

        # Combine docs & scores
        doc_score_pairs = list(zip(texts, scores))

        # Sort by decreasing score
        doc_score_pairs = sorted(
            doc_score_pairs, key=lambda x: x[1], reverse=True)

        # Output passages & scores
        for doc, score in doc_score_pairs:
            print(score, doc)

    def embed_texts_with_custom_tokenizer(self, texts: list[str]):
        model = AutoModel.from_pretrained("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
        tokenizer = retrieve_tokenizer()

        # Tokenize sentences
        encoded_input = tokenizer(
            texts, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = model(**encoded_input, return_dict=True)

        # Perform pooling
        embeddings = self.mean_pooling(
            model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings

    # Mean Pooling - Take average of all tokens
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(
            -1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


embedder = Embeddder()

if __name__ == '__main__':
    texts = [
        "Žalobce se domáhal vydání rozhodnutí, jímž by soud uložil žalovanému povinnost zaplatit mu v záhlaví uvedenou částku s příslušenstvím s tím, že se jedná o náklady za odběr krve, klinické vyšetření hladiny návykové látky v krvi a náklady na dopravu dne [datum], když u žalovaného byla prokázána přítomnost metamfetaminu v jeho krvi. Žalovaný byl vyzván k zaplacení svého dluhu písemnou výzvou nejpozději do [datum]. Žalovaný na svůj dluh přes výzvu k úhradě nic neuhradil.",
        "Podle žaloby, žalobkyně a žalovaný mezi sebou distančně prostřednictvím elektronických prostředků uzavřeli dne [datum] rámcovou smlouvu a následně Úvěrovou smlouvu. K uzavření obou smluv mělo dojít prostřednictvím internetových stránek žalobkyně [anonymizováno]. Na základě smlouvy o úvěru žalobkyně poskytla žalovanému na jeho žádost peněžní prostředky v celkové výši 5 000 Kč. Žalovaný měl podle smlouvy žalobkyni vrátit poskytnutou částku, poplatek za poskytnutí úvěru ve výši 165 Kč, Částku 5 000 Kč zaslala žalobkyně na účet žalovaného dne [datum]. Žalovaný podle tvrzení žalobkyně měl splatit úvěr do 30 dnů. Splatnost byla prodloužena platbou ve výši 4 Kč dne [datum]. Žalovanému byl účtován poplatek za prodloužení splatnosti ve výši 495 Kč a dále mu byla účtována smluvní pokuta ve výši 3 % nezaplacené jistiny (ve výši 150 Kč) a dále poplatky za vymáhání ve výši 3 x 100 Kč. Požadován je i poplatek ve výši 249 Kč za výběr na terminálu [příjmení].",
        """
4. Soud má za zjištěné, že účastníci uzavřeli dne 15. 11. 2018 dvě účastnické smlouvy, na jejichž základě poskytla žalobkyně uživatelce (žalované) kromě předmětných služeb (DIGI TV a DIGI Internet) též koncová zařízení (STB a modem), která se žalovaná zavázala pod hrozbou pokuty 5 000 Kč vrátit do 10 dnů od ukončení smlouvy. Žalovaná za poskytované služby neplatila, proto žalobkyně dne 30. 4. 2019 ukončila poskytování služeb. Přes výzvy obsahující náhradní lhůty žalovaná koncová zařízení nevrátila.
5. Zatímco samotná existence smluvního vztahu a spory z něj vyplývající jsou řešeny zákonem č. 127/2005 Sb., o elektronických komunikacích a k jejich rozhodování je příslušný Český telekomunikační úřad, výpůjčka věci je soukromoprávním vztahem a příslušný k rozhodování o smluvní pokutě plynoucí z porušení povinností vztahujících se k výpůjčce je tedy soud, což ostatně konstatoval zvláštní senát zřízený podle zákona č. 131/2002 Sb., o rozhodování některých kompetenčních ve svém usnesení ze dne 27. 7. 2011, č.j. Konf 49/2011 - 11.
6. V projednávaném případě žalobkyně prokázala uzavření smluv o poskytování služeb elektronických komunikacích a předání elektronických zařízení žalované. K projednání sporu je ve výše uvedeném smyslu příslušný zdejší soud.
        """,
        """
3. Právně byla věc posouzena v souladu s ust. § 2 písm. n) zákona č. 127/2005 Sb., o elektronických komunikacích, se službou elektronických komunikací rozumí služba obvykle poskytovaná za úplatu, která spočívá zcela nebo převážně v přenosu signálů po sítích elektronických komunikací, včetně telekomunikačních služeb a přenosových služeb v sítích používaných pro rozhlasové a televizní vysílání a v sítích kabelové televize, s výjimkou služeb, které nabízejí obsah prostřednictvím sítí a služeb elektronických komunikací nebo vykonávají redakční dohled nad obsahem přenášeným sítěmi a poskytovaným službami elektronických komunikací; nezahrnuje služby informační společnosti, které nespočívají zcela nebo převážně v přenosu signálů po sítích elektronických komunikací.
"""
    ]

    query = "Uzavření smlouvy"

    custom_score = embedder.score(texts, query)
    print('---')
    custom_score = embedder.score(texts, query, False)


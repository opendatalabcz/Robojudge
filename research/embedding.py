from sentence_transformers import SentenceTransformer

from transformers import AutoModel
import torch
import torch.nn.functional as F

from robojudge.utils.settings import settings
from robojudge.components.chunker import split_text_into_embeddable_chunks
# from research.tokenizer import retrieve_tokenizer


class Embeddder:
    model: SentenceTransformer

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            model_name_or_path="all-MiniLM-L6-v2")
        print("Max Sequence Length:", self.model.max_seq_length)

    def embed_texts(self, texts: list[str]):
        return self.model.encode(texts).tolist()


if __name__ == '__main__':
    # import pathlib
    # long_file = pathlib.Path('./datasets/answering/reference/949_2.txt').read_text()
    # import tiktoken

    long_file = """
Soud při rozhodování o pohledávce za předmětnou smlouvou postupoval soud podle ustanovení §§ 497, 1746 odst. 2 a ustanovení § 1828 a násl. zák. č. 89/2012 Sb. občanský zákoník (dále jen o.z.), dále podle dopadajících ustanovení zák. č. 458/2000 Sb. o podmínkách podnikání a o výkonu státní správy v energetických odvětvích a o změně některých zákonů (energetický zákon) ve spojení s dopadajícími ustanoveními cenového rozhodnutí ERU pro daná období, podle samotného smluvního ujednání účastníků a podle ustanovení § 1968 a násl. o.z. Soud žalobě jako důvodné vyhověl a a žalované uložil dlužnou částku, zákonný úrok z prodlení a poplatky za výzvy k zaplacení k rukám žalobkyně zaplatit (výrok sub. I).
"""

    # tokenizer = tik
    # token.get_encoding("cl100k_base")

    # print(len(tokenizer.encode(long_file)))

    chunked_text1 = split_text_into_embeddable_chunks(long_file)

    embedder = Embeddder()
    embeddings_long = embedder.embed_texts(chunked_text1)
    
    chunked_text2 = split_text_into_embeddable_chunks(long_file, 257)
    embeddings_short = embedder.embed_texts(chunked_text2)

    print(embeddings_short[0])
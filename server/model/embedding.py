from sentence_transformers import SentenceTransformer

from server.utils.settings import settings


class Embeddder:
    model: SentenceTransformer

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            model_name_or_path=settings.EMBEDDING_MODEL, cache_folder=settings.EMBEDDING_CACHE_DIR)

    def embed_texts(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True).tolist()


embedder = Embeddder()

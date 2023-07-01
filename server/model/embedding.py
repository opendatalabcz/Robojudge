from sentence_transformers import SentenceTransformer

from server.utils.settings import settings


class Embeddder:
    model: SentenceTransformer

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            model_name_or_path=settings.EMBEDDING_MODEL, cache_folder=settings.EMBEDDING_CACHE_DIR)

    def embed_text(self, text: str | list[str]):
        return self.model.encode(text)


embedder = Embeddder()

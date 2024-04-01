# Inspired by  https://github.com/openai/chatgpt-retrieval-plugin :: chunks.py

from typing import Optional


from langchain.schema import Document
import more_itertools

from robojudge.utils.settings import settings
from robojudge.utils.gpt_tokenizer import tokenizer


class TextChunker:
    MIN_CHUNK_LENGTH_TO_EMBED = 5  # Discard chunks shorter than this
    EMBEDDINGS_BATCH_SIZE = 16  # The number of embeddings to request at a time
    MAX_NUM_CHUNKS = 10000  # The maximum number of chunks to generate from a text
    MIN_CHUNK_SIZE_CHARS = 100  # The minimum size of each text chunk in characters

    LLM_CHUNK_SIZE = 4096 - 500

    @classmethod
    def split_text_into_embeddable_chunks(
        cls, text: str, chunk_size: Optional[int] = settings.EMBEDDING_CHUNK_SIZE
    ) -> list[str]:
        if not text or text.isspace():
            return []

        tokens = tokenizer.encode(text, disallowed_special=())

        chunks = []
        num_chunks = 0

        while tokens and num_chunks < cls.MAX_NUM_CHUNKS:
            chunk = tokens[:chunk_size]
            chunk_text = tokenizer.decode(chunk)

            # Skip the chunk if it is empty or whitespace
            if not chunk_text or chunk_text.isspace():
                # Remove the tokens corresponding to the chunk text from the remaining tokens
                tokens = tokens[len(chunk) :]
                continue

            # Find the last period or punctuation mark in the chunk
            last_punctuation = max(
                chunk_text.rfind("."),
                chunk_text.rfind("?"),
                chunk_text.rfind("!"),
                chunk_text.rfind("\n"),
            )

            # If there is a punctuation mark, and the last punctuation index is before MIN_CHUNK_SIZE_CHARS
            if last_punctuation != -1 and last_punctuation > cls.MIN_CHUNK_SIZE_CHARS:
                # Truncate the chunk text at the punctuation mark
                chunk_text = chunk_text[: last_punctuation + 1]

            # Remove any newline characters and strip any leading or trailing whitespace
            chunk_text_to_append = chunk_text.replace("\n", " ").strip()
            if len(chunk_text_to_append) > cls.MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(chunk_text_to_append)

            # Remove the tokens corresponding to the chunk text from the remaining tokens
            tokens = tokens[len(tokenizer.encode(chunk_text, disallowed_special=())) :]

            num_chunks += 1

        # Handle the remaining tokens
        if tokens:
            remaining_text = tokenizer.decode(tokens).replace("\n", " ").strip()
            if len(remaining_text) > cls.MIN_CHUNK_LENGTH_TO_EMBED:
                chunks.append(remaining_text)

        return chunks

    @classmethod
    def split_text_into_llm_chunks(cls, text: str):
        chunks = []

        tokens = tokenizer.encode(text)
        if len(tokens) <= cls.LLM_CHUNK_SIZE:
            chunks.append(Document(page_content=text))
        else:
            split_tokens = more_itertools.chunked(tokens, cls.LLM_CHUNK_SIZE)
            chunks.extend(
                [
                    Document(page_content=tokenizer.decode(token_batch))
                    for token_batch in split_tokens
                ]
            )

        return chunks

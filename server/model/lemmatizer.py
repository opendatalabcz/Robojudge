import httpx
import more_itertools
import asyncio

from server.utils.settings import settings
from server.utils.logger import logging


class Lemmatizer:
    def __init__(self) -> None:
        ...

    async def lemmatize_text(self, text: str) -> list[str]:
        lemmatize_tasks = []
        # This is not tokenization yet so we can simply split on whitespace
        for text_chunk in more_itertools.chunked(text.split(' '), settings.TOKENIZER_INPUT_LENGTH):
            lemmatize_tasks.append(self.call_lemma_api(' '.join(text_chunk)))

        texts = await asyncio.gather(*lemmatize_tasks)

        result = []
        for text in texts:
            result.extend(text)
        return ' '.join(result)

    async def call_lemma_api(self, text: str) -> str:
        tokenize_params = {
            "data": text,
            "output": "json",
            "model": settings.TOKENIZER_MODEL,
            "guesser": "yes",
        }

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(settings.TOKENIZER_URL, params=tokenize_params)
                tokens = res.json().get('result')
                return [token.get('lemma', 'token') for sentence in tokens for token in sentence]
            except Exception as e:
                logging.exception(f'Error while lemmatizing text "{text}":')

lemmatizer = Lemmatizer()

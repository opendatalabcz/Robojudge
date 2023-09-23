import re

from ufal.morphodita import Tokenizer as MorphTokenizer, Forms, TokenRanges
from tokenizers import NormalizedString, PreTokenizedString

from robojudge.utils.settings import settings
from robojudge.utils.logger import logging

# TODO: Add more abbrevs if you find them
STATUTES = [
    'o.(\s+)s.(\s+)ř.',
]


class Pretokenizer:
    abbrev_regex = re.compile(f'({"|".join(STATUTES)})')

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        forms = Forms()
        tokens = TokenRanges()
        tokenizer = MorphTokenizer.newCzechTokenizer()

        result = []

        text = cls.preprocess(text)

        tokenizer.setText(text)
        while tokenizer.nextSentence(forms, tokens):
            for token in forms:
                result.append(token)

        return result

    @classmethod
    def preprocess(cls, text: str) -> str:
        text = cls.collect_legal_abbreviations(text)
        text = cls.remove_anonymized_brackets(text)
        return text

    @classmethod
    def postprocess(cls, text: str) -> str:
        ...

    @classmethod
    def collect_legal_abbreviations(cls, text: str) -> str:
        return re.sub(cls.abbrev_regex, lambda x: x.group(
            1).replace('.', '').replace(' ', '').upper(), text)

    @classmethod
    def remove_anonymized_brackets(cls, text: str) -> str:
        return re.sub(re.compile(r'\[|\]'), '', text)


class HuggingFaceCustomCzechPretokenizer:
    def split_str(self, i: int, normalized_string: NormalizedString) -> list[NormalizedString]:
        tokens = Pretokenizer.tokenize(str(normalized_string))
        return [NormalizedString(token) for token in tokens]

    def pre_tokenize(self, pretok: PreTokenizedString):
        # Let's call split on the PreTokenizedString to split using `self.jieba_split`
        pretok.split(self.split_str)

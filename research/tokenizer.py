from pathlib import Path

from research.pretokenizer import HuggingFaceCustomCzechPretokenizer
from robojudge.utils.logger import logging

from tokenizers.pre_tokenizers import PreTokenizer, BertPreTokenizer
from tokenizers import Tokenizer
from transformers import PreTrainedTokenizerFast
from tokenizers import (
    decoders,
    models,
    normalizers,
    processors,
    trainers,
    Tokenizer,
)

TOKENIZER_PATH = Path('embedding_models/tokenizer')
TOKENIZER_TRAINING_SET_PATH = Path('datasets/tokenizer')

UNKNOWN_TOKEN = '[UNK]'
CLS_TOKEN = '[CLS]'
SEP_TOKEN = '[SEP]'
PAD_TOKEN = "[PAD]"
MASK_TOKEN = "[MASK]"

SPECIAL_TOKENS = [UNKNOWN_TOKEN, PAD_TOKEN, CLS_TOKEN, SEP_TOKEN, MASK_TOKEN]


def retrieve_tokenizer(recreate_tokenizer=False) -> PreTrainedTokenizerFast:
    if TOKENIZER_PATH.exists() and not recreate_tokenizer:
        logging.info(
            'Tokenizer for the embedding model already exists, returning that one.')
        tokenizer = PreTrainedTokenizerFast.from_pretrained(TOKENIZER_PATH)
        load_custom_tokenizer(tokenizer)
        return tokenizer

    logging.info('Creating and training a new tokenizer, please be patient.')

    tokenizer = create_tokenizer()

    train_tokenizer(tokenizer)

    add_postprocessing(tokenizer)

    wrapped_tokenizer = wrap_and_export_tokenizer(tokenizer)

    return wrapped_tokenizer


def create_tokenizer():
    tokenizer = Tokenizer(models.WordPiece(unk_token=UNKNOWN_TOKEN))

    tokenizer.normalizer = normalizers.Sequence(
        [normalizers.NFD(), normalizers.Lowercase()])

    load_custom_tokenizer(tokenizer)

    return tokenizer


def train_tokenizer(tokenizer: Tokenizer):
    trainer = trainers.WordPieceTrainer(
        vocab_size=25000, special_tokens=SPECIAL_TOKENS)

    training_corpus = list(Path.iterdir(TOKENIZER_TRAINING_SET_PATH))

    tokenizer.train([str(path) for path in training_corpus], trainer=trainer)


def add_postprocessing(tokenizer: Tokenizer):
    beginning_token_id = tokenizer.token_to_id(CLS_TOKEN)
    end_token_id = tokenizer.token_to_id(SEP_TOKEN)

    tokenizer.post_processor = processors.TemplateProcessing(
        single=f"{CLS_TOKEN}:0 $A:0 {SEP_TOKEN}:0",
        pair=f"{CLS_TOKEN}:0 $A:0 {SEP_TOKEN}:0 $B:1 {SEP_TOKEN}:1",
        special_tokens=[(CLS_TOKEN, beginning_token_id),
                        (SEP_TOKEN, end_token_id)],
    )

    tokenizer.decoder = decoders.WordPiece(prefix='##')


def wrap_and_export_tokenizer(tokenizer: Tokenizer):
    tokenizer.pre_tokenizer = BertPreTokenizer()

    wrapped_tokenizer = PreTrainedTokenizerFast(
        tokenizer_object=tokenizer,
        unk_token=UNKNOWN_TOKEN,
        pad_token=PAD_TOKEN,
        cls_token=CLS_TOKEN,
        sep_token=SEP_TOKEN,
        mask_token=MASK_TOKEN,
    )

    wrapped_tokenizer.save_pretrained(TOKENIZER_PATH)
    logging.info(f'Tokenizer successfully saved to: {TOKENIZER_PATH}')

    load_custom_tokenizer(wrapped_tokenizer)

    return wrapped_tokenizer


def load_custom_tokenizer(tokenizer: Tokenizer):
    # Custom tokenizer cannot be serialized and is replaced with a dummy
    # We have to add it back here
    tokenizer.pre_tokenizer = PreTokenizer.custom(
        HuggingFaceCustomCzechPretokenizer())
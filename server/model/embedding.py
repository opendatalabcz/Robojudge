from sentence_transformers import SentenceTransformer

from tokenizers.pre_tokenizers import PreTokenizer
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

import asyncio

from server.utils.settings import settings
from server.model.lemmatizer import lemmatizer

from tokenizers import Tokenizer, Regex, NormalizedString, PreTokenizedString
from tokenizers.models import BPE, WordPiece
from tokenizers.pre_tokenizers import PreTokenizer
from tokenizers.normalizers import Normalizer
from tokenizers.decoders import Decoder

class Embeddder:
    model: SentenceTransformer

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            model_name_or_path=settings.EMBEDDING_MODEL, cache_folder=settings.EMBEDDING_CACHE_DIR)

    def embed_texts(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True).tolist()


embedder = Embeddder()

class JiebaPreTokenizer:
    def jieba_split(self, i: int, normalized_string: NormalizedString) -> list[NormalizedString]:
        splits = []
        # # we need to call `str(normalized_string)` because jieba expects a str,
        # # not a NormalizedString
        #     splits.append(normalized_string[start:stop])

        # return splits
        # We can also easily do it in one line:
        # return asyncio.run(lemmatizer.lemmatize_text(str(normalized_string)))
        return ['hhhhhhh']

    def pre_tokenize(self, pretok: PreTokenizedString):
        # Let's call split on the PreTokenizedString to split using `self.jieba_split`
        pretok.split(self.jieba_split)


#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Sentences we want sentence embeddings for
sentences = ['Tohle je česká věta vole', 'Each sentence is converted']

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
# tokenizer = Tokenizer(WordPiece())
# tokenizer.pre_tokenizer = PreTokenizer.custom(JiebaPreTokenizer())
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')


# Tokenize sentences
encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
print(encoded_input)
print(tokenizer.decode(encoded_input['input_ids'][0]))

# # Compute token embeddings
# with torch.no_grad():
#     model_output = model(**encoded_input)

# # Perform pooling
# sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

# # Normalize embeddings
# sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

# print("Sentence embeddings:")
# print(sentence_embeddings)
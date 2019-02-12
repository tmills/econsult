import numpy as np
import re

import torch
from typing import List, Union
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentLSTMEmbeddings, ELMoEmbeddings, TokenEmbeddings
from flair.data import Sentence, Token

    
class BackOffEmbeddings(TokenEmbeddings):

    def __init__(self, embeddings1: WordEmbeddings, embeddings2: WordEmbeddings, detach: bool = True):
        """The constructor takes a pair of embeddings to be combined."""
        super().__init__()

        self.embeddings1 = embeddings1
        self.embeddings2 = embeddings2

        # IMPORTANT: add embeddings as torch modules
        self.add_module('backoff_embedding_1', embeddings1)
        self.add_module('backoff_embedding_2', embeddings1)

        self.detach: bool = detach
        self.name: str = 'Backoff'
        self.static_embeddings: bool = True

        self.__embedding_type: str = embeddings1.embedding_type

        assert embeddings1.embedding_length == embeddings2.embedding_length

        self.__embedding_length: int = embeddings1.embedding_length

    @property
    def embedding_length(self) -> int:
        return self.__embedding_length

    def embed(self, sentences: Union[Sentence, List[Sentence]], static_embeddings: bool = True):
        # if only one sentence is passed, convert to list of sentence
        if type(sentences) is Sentence:
            sentences = [sentences]

        # First do the normal (backoff) embeddings:
        self.embeddings1.embed(sentences)
        name = self.embeddings1.name

        # Then iterate over tokens and replace if we find one:
        for i, sentence in enumerate(sentences):
            for token, token_idx in zip(sentence.tokens, range(len(sentence.tokens))):
                token: Token = token

                if 'field' not in self.embeddings2.__dict__ or self.embeddings2.field is None:
                    word = token.text
                else:
                    word = token.get_tag(self.embeddings2.field).value

                if word in self.embeddings2.precomputed_word_embeddings:
                    word_embedding = self.embeddings2.precomputed_word_embeddings[word]
                elif word.lower() in self.embeddings2.precomputed_word_embeddings:
                    word_embedding = self.embeddings2.precomputed_word_embeddings[word.lower()]
                elif re.sub(r'\d', '#', word.lower()) in self.embeddings2.precomputed_word_embeddings:
                    word_embedding = self.embeddings2.precomputed_word_embeddings[re.sub(r'\d', '#', word.lower())]
                elif re.sub(r'\d', '0', word.lower()) in self.embeddings2.precomputed_word_embeddings:
                    word_embedding = self.embeddings2.precomputed_word_embeddings[re.sub(r'\d', '0', word.lower())]
                else:
                    word_embedding = None

                if not word_embedding is None:
                    word_embedding = torch.FloatTensor(word_embedding)
                    token.set_embedding(name, word_embedding)

    def _add_embeddings_internal(self, sentences: List[Sentence]) -> List[Sentence]:
        raise Exception("This is not implemented")
        # for i, sentence in enumerate(sentences):

        #     for token, token_idx in zip(sentence.tokens, range(len(sentence.tokens))):
        #         token: Token = token

        #         if 'field' not in self.embeddings.__dict__ or self.embeddings.field is None:
        #             word = token.text
        #         else:
        #             word = token.get_tag(self.embeddings.field).value

        #         if word in self.embeddings.precomputed_word_embeddings:
        #             word_embedding = self.embeddings.precomputed_word_embeddings[word]
        #         elif word.lower() in self.embeddings.precomputed_word_embeddings:
        #             word_embedding = self.embeddings.precomputed_word_embeddings[word.lower()]
        #         elif re.sub(r'\d', '#', word.lower()) in self.embeddings.precomputed_word_embeddings:
        #             word_embedding = self.embeddings.precomputed_word_embeddings[re.sub(r'\d', '#', word.lower())]
        #         elif re.sub(r'\d', '0', word.lower()) in self.embeddings.precomputed_word_embeddings:
        #             word_embedding = self.embeddings.precomputed_word_embeddings[re.sub(r'\d', '0', word.lower())]
        #         else:
        #             return self.

        #         word_embedding = torch.FloatTensor(word_embedding)

        #         token.set_embedding(self.name, word_embedding)

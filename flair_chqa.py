#!/usr/bin/env python3.6
#
#######################
# flair_chqa.py
# Train and evaluate the flair embeddings on the chqa
# focus task. 
# This code is borrowed from:
# https://github.com/zalandoresearch/flair/blob/master/resources/docs/TUTORIAL_TRAINING_A_MODEL.md
#######################

import sys

from flair.data import TaggedCorpus
from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings
from typing import List


def main(args):
    if len(args) < 1:
        sys.stderr.write('One required argument: <data dir>\n')
        sys.exit(-1)
    
    # 1. get the corpus
    column_format = {0:'word', 1:'pos', 2:'focus'}
    corpus: TaggedCorpus = NLPTaskDataFetcher.fetch_column_corpus(args[0],
        column_format,
        'train.txt',
        'test.txt',
        dev_file='dev.txt')
    print(corpus)

    # 2. what tag do we want to predict?
    tag_type = 'focus'

    # 3. make the tag dictionary from the corpus
    tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)
    print(tag_dictionary.idx2item)

    # 4. initialize embeddings
    embedding_types: List[TokenEmbeddings] = [

        WordEmbeddings('glove'),

        # comment in this line to use character embeddings
        # CharacterEmbeddings(),

        # comment in these lines to use contextual string embeddings
        # CharLMEmbeddings('news-forward'),
        # CharLMEmbeddings('news-backward'),
    ]

    embeddings: StackedEmbeddings = StackedEmbeddings(embeddings=embedding_types)

    # 5. initialize sequence tagger
    from flair.models import SequenceTagger

    tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                            embeddings=embeddings,
                                            tag_dictionary=tag_dictionary,
                                            tag_type=tag_type,
                                            use_crf=True)

    # 6. initialize trainer
    from flair.trainers import SequenceTaggerTrainer

    trainer: SequenceTaggerTrainer = SequenceTaggerTrainer(tagger, corpus, test_mode=True)

    # 7. start training
    trainer.train('resources/taggers/chqa-focus',
                learning_rate=0.1,
                mini_batch_size=32,
                max_epochs=150)

if __name__ == '__main__':
    main(sys.argv[1:])

import sys
from os.path import join, dirname, basename
from typing import List

from flair.data import TaggedCorpus, Sentence
from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentLSTMEmbeddings, ELMoEmbeddings
from flair.models import TextClassifier
from flair.trainers import ModelTrainer
import argparse

from sklearn.model_selection import KFold
import numpy as np

parser = argparse.ArgumentParser(description='Flair trainer for classifying sentences in consumer health questions')
parser.add_argument('-d', '--data-file', help='Flair-formatted directory with gold standard data')
parser.add_argument('-k', '--num-folds', required=False, default=5, help='Number of folds to use in cross-validation')

def main(args):
    args = parser.parse_args()

    # 1. get the corpus
    sents: List[Sentence] = NLPTaskDataFetcher.read_text_classification_file(args.data_file)
    corpus = TaggedCorpus(sents, None, None)

    # 2. create the label dictionary
    label_dict = corpus.make_label_dictionary()

    # 3. make a list of word embeddings
    word_embeddings = [WordEmbeddings('glove'),

                    # comment in flair embeddings for state-of-the-art results 
                    # FlairEmbeddings('news-forward'),
                    # FlairEmbeddings('news-backward'),
                    # ELMoEmbeddings()
                    ]

    # 4. init document embedding by passing list of word embeddings
    document_embeddings: DocumentLSTMEmbeddings = DocumentLSTMEmbeddings(word_embeddings,
                                                                        hidden_size=128,
                                                                        reproject_words=True,
                                                                        reproject_words_dimension=64,
                                                                        )

    # 5. split the training data into folds
    num_folds = args.num_folds
    kf = KFold(n_splits=num_folds)
    kf.get_n_splits()

    # 6. iterate over folds:
    total_acc = 0
    for train_index, test_index in kf.split(corpus.train):
        # 6a. initialize the text classifier trainer
        classifier = TextClassifier(document_embeddings, label_dictionary=label_dict, multi_label=False)
        split_traindev = np.array(corpus.train)[train_index].tolist()
        traindev_size = len(split_traindev)
        train_dev_splitpoint = int(0.9*traindev_size)
        split_train = split_traindev[:train_dev_splitpoint]
        split_dev = split_traindev[train_dev_splitpoint:]

        split_test = np.array(corpus.train)[test_index].tolist()
        split_corpus = TaggedCorpus(split_train, dev=split_dev, test=split_test)

        trainer = ModelTrainer(classifier, split_corpus)

        model_out = 'resources/classifiers/sentence-classification/glove_xfold'
        results = trainer.train(model_out,
                learning_rate=0.1,
                mini_batch_size=32,
                anneal_factor=0.5,
                patience=5,
                max_epochs=100)
        fold_acc = results['test_score']
        total_acc += fold_acc
        print("Finished fold with accuracy %f" % (fold_acc))
    total_acc /= num_folds

    print("FInished with total cross-fold accuracy of %f" % (total_acc))



if __name__ == '__main__':
    main(sys.argv[1:])

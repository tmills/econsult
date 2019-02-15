import sys
import os
from os.path import join, dirname, basename, isfile
from typing import List
import tempfile

from flair.data import TaggedCorpus, Sentence
from flair.data_fetcher import NLPTaskDataFetcher, NLPTask
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentLSTMEmbeddings, ELMoEmbeddings
from flair.models import TextClassifier
from flair.trainers import ModelTrainer
import argparse

from sklearn.model_selection import KFold
import numpy as np

from backoff import BackOffEmbeddings

parser = argparse.ArgumentParser(description='Flair trainer for classifying sentences in consumer health questions')
parser.add_argument('-f', '--data-file', required=True, help='Flair-formatted file with gold standard data')
parser.add_argument('-k', '--num-folds', required=False, default=5, help='Number of folds to use in cross-validation')
modes = ('glove', 'flair', 'cui_svd', 'cui_proj')
parser.add_argument('-m', '--method', required=True, choices=modes, help='Method to use: glove=Glove embeddings alone, flair=glove+Flair contextual embeddings, cui_svd=glove+cuis reduced with SVD, cui_proj=glove+cuis projected with mikolov')
# parser.add_argument('-m', '--multi', default=False, action="store_true", help='Whether this is a multi-label problem or not')

def main(args):
    args = parser.parse_args()

    # 0. Make a list of word embeddings
    if args.method == 'glove':
        word_embeddings = [WordEmbeddings('glove')]
    elif args.method == 'flair':
        word_embeddings = [WordEmbeddings('glove'),
                    FlairEmbeddings('news-forward'),
                    FlairEmbeddings('news-backward')]
    elif args.method == 'cui_svd':
        word_embeddings = [BackOffEmbeddings( WordEmbeddings('glove'),
                                              WordEmbeddings('resources/embeddings/cui2vec100.npy'))]
    elif args.method == 'cui_proj':
        word_embeddings = [BackOffEmbeddings( WordEmbeddings('glove'),
                                              WordEmbeddings('resources/embeddings/cui2vec_projected_100.gensim'))]
    else:
        raise Exception("Received optino for method %s that cannot be interpreted." % (args.method))

    if 'bg' in args.data_file:
        multi = True
        print("Running in multiple label setting because 'bg' was in the data file name %s" % (args.data_file))
    else:
        multi = False

    # 1. get the corpus
    sents: List[Sentence] = NLPTaskDataFetcher.read_text_classification_file(args.data_file)
    corpus = TaggedCorpus(sents, None, None)

    # 2. create the label dictionary
    label_dict = corpus.make_label_dictionary()

    # 3. split the training data into folds
    num_folds = args.num_folds
    seed = 719
    kf = KFold(n_splits=num_folds, random_state=seed)
    kf.get_n_splits()

    # 4. iterate over folds:
    total_acc = 0
    fold = 1
    for train_index, test_index in kf.split(corpus.train):
        # 4a. initialize the text classifier trainer
        split_traindev = np.array(corpus.train)[train_index].tolist()
        traindev_size = len(split_traindev)
        train_dev_splitpoint = int(0.9*traindev_size)
        split_train = split_traindev[:train_dev_splitpoint]
        split_dev = split_traindev[train_dev_splitpoint:]

        split_test = np.array(corpus.train)[test_index].tolist()
        split_corpus = TaggedCorpus(split_train, dev=split_dev, test=split_test)

        print("After split, size of splits: train=%d, dev=%d, test=%d" % 
                (len(split_train), len(split_dev), len(split_test)))

        # 4b. do training:
        with tempfile.TemporaryDirectory() as model_dir:
            # init document embedding by passing list of word embeddings
            document_embeddings: DocumentLSTMEmbeddings = DocumentLSTMEmbeddings(word_embeddings,
                                                                        hidden_size=128,
                                                                        reproject_words=True,
                                                                        reproject_words_dimension=64,
                                                                        )
            classifier = TextClassifier(document_embeddings, label_dictionary=label_dict, multi_label=multi)
            trainer = ModelTrainer(classifier, split_corpus)

            results = trainer.train(model_dir,
                    learning_rate=0.1,
                    mini_batch_size=32,
                    anneal_factor=0.5,
                    patience=5,
                    max_epochs=100)

        fold_acc = results['test_score']
        total_acc += fold_acc
        print(f"Finished fold {fold} with accuracy {fold_acc}")
        fold += 1
    total_acc /= num_folds

    print("Finished with total cross-fold accuracy of %f" % (total_acc))


if __name__ == '__main__':
    main(sys.argv[1:])

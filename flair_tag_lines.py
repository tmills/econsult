#!/usr/bin/env python3.6
#
#######################

import sys

from flair.data import Sentence
from flair.models import SequenceTagger
from nltk import word_tokenize, sent_tokenize
import re

def main(args):
    if len(args) < 1:
        sys.stderr.write('One required argument: <model file>\n')
        sys.exit(-1)
    
    tagger = SequenceTagger.load_from_file(args[0])

    for line in sys.stdin:
        line = re.sub(r'([a-zA-Z])\.([a-zA-Z])', r'\1. \2', line.rstrip())

        sentences = sent_tokenize(line.rstrip())
        for sent_str in sentences:
            sentence = Sentence(' '.join(word_tokenize(sent_str)))
            tagger.predict(sentence)
            print(sentence.to_tagged_string())

if __name__ == '__main__':
    main(sys.argv[1:])

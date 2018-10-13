#!/usr/bin/env python3.6
#
#######################

import sys

from flair.data import Sentence
from flair.models import SequenceTagger

def main(args):
    if len(args) < 1:
        sys.stderr.write('One required argument: <model file>\n')
        sys.exit(-1)
    
    tagger = SequenceTagger.load_from_file(args[0])

    for line in sys.stdin:
        sentence = Sentence(line.rstrip())
        tagger.predict(sentence)
        print(sentence.to_tagged_string())

if __name__ == '__main__':
    main(sys.argv[1:])


from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec

import sys

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required arguments: <line file> <output file>\n')
        sys.exit(-1)

    lines = LineSentence(args[0])
    model = Word2Vec(lines, workers=4, size=100, window=5)
    model.wv.save(args[1])

if __name__ == '__main__':
    main(sys.argv[1:])


from scipy.sparse.linalg import svds
import gensim
from gensim.models.keyedvectors import BaseKeyedVectors
import numpy as np

import sys

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required arguments: <path to cui2vec gensim file> <output filename (.npy)>\n')
        sys.exit(-1)

    gs_vecs = gensim.models.keyedvectors.BaseKeyedVectors.load(args[0])
    embed = np.matrix( np.zeros( (len(gs_vecs.vocab), 500)))
    vocab_size = len(gs_vecs.vocab)
    for word_ind in range(vocab_size):
        cui = gs_vecs.index2word[word_ind]
        vec = gs_vecs.word_vec(cui)
        embed[word_ind,:] += vec

    [U, s, Vh] = svds(embed, k=100)
    S = np.diag(s)
    recon = np.dot(U, S)

    new_mat = BaseKeyedVectors(100)
    vocab_list = list(gs_vecs.vocab.keys())
    new_mat.add(vocab_list, recon)
    new_mat.save(args[1])



if __name__ == '__main__':
    main(sys.argv[1:])
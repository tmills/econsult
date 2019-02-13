from scipy.sparse.linalg import svds
import gensim
from gensim.models.keyedvectors import BaseKeyedVectors
import numpy as np

import sys
import tempfile

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required arguments: <path to cui2vec gensim file> <output filename (.npy)>\n')
        sys.exit(-1)

    embed_dims = 100
    gs_vecs = gensim.models.keyedvectors.BaseKeyedVectors.load(args[0])
    embed = np.matrix( np.zeros( (len(gs_vecs.vocab), 500)))
    vocab_size = len(gs_vecs.vocab)
    for word_ind in range(vocab_size):
        cui = gs_vecs.index2word[word_ind]
        vec = gs_vecs.word_vec(cui)
        embed[word_ind,:] += vec

    [U, s, Vh] = svds(embed, k=embed_dims)
    S = np.diag(s)
    recon = np.dot(U, S)

    tf = tempfile.NamedTemporaryFile(mode='wt')
    tf.write('%d %d\n' % (vocab_size, embed_dims))
    for cui_ind in range(vocab_size):
        cui = gs_vecs.index2word[cui_ind]
        vec = list(recon[cui_ind,:])
        str_vec = [str(x) for x in vec]
        tf.write('%s %s\n' % (cui, ' '.join(str_vec)))

    tf.seek(0)
    gs_new_vecs = gensim.models.KeyedVectors.load_word2vec_format(tf.name)
    gs_new_vecs.save(args[1])


if __name__ == '__main__':
    main(sys.argv[1:])
#!/usr/bin/env python3

# This script converts the cui vectors in the CSV file released by Andrew Beam here:
# http://cui2vec.dbmi.hms.harvard.edu/
# to a numpy format readable by Flair for its embeddings class

import os
import sys
import numpy as np
import csv
import pickle
import tempfile
import gensim

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required arguments: <path to cui2vec csv file> <output filename (.npy)>\n')
        sys.exit(-1)

    vec_list = []
    cui_list = []
    with open(args[0], 'r') as f:
        vec_reader = csv.reader(f, delimiter=',')
        for row in vec_reader:
            cui = row[0]
            if len(cui) <= 0:
                continue
            cui_list.append(cui)
            vec = row[1:]
            vec_list.append(vec)
    
    # First write a temporary file in w2v format:
    tf = tempfile.NamedTemporaryFile(mode='wt')
    tf.write('%d %d\n' % (len(vec_list), len(vec_list[0])))
    for row,vec in enumerate(vec_list):
        tf.write('%s %s\n' % (cui_list[row], ' '.join(vec)))

    tf.seek(0)
    gs_vecs = gensim.models.KeyedVectors.load_word2vec_format(tf.name)
    gs_vecs.save(args[1])

    tf.close()


if __name__ == '__main__':
    main(sys.argv[1:])

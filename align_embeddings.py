####################
# align_embeddings.py
# Learns a linear mapping between a cui embeddings and word embeddings list, based on UMLS synonyms
###################

import gensim
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as cos
import sys
import tempfile
import torch
import torch.nn as nn
import torch.optim as optim

def build_cuiword_pairs(mrc_fn, cui_vecs, word_vecs):
    pairs = []
    with open(mrc_fn, 'r') as f:
        for line in f.readlines():
            fields = line.split('|')
            cui = fields[0]
            lang = fields[1]
            vocab = fields[11]
            preferred_term = fields[14].lower()
            if cui in cui_vecs.vocab:
                terms = preferred_term.split()
                if len(terms) == 1 and terms[0] in word_vecs:
                    pairs.append( (cui, terms[0]) )
    
    return pairs

def main(args):
    if len(args) < 4:
        sys.stderr.write('Four required arguments: <cui vecs path> <glove vecs path> <MRCONSO file> <output file>\n')
        sys.exit(-1)

    num_epochs = 500
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    example_pairs = [ ('C0021400', 'influenza'),
                      ('C0006826', 'cancer'),
                      ('C0004057', 'aspirin'),
                      ('C0027497', 'nausea'),
                      ('C0030193', 'pain') ]
   
    print("Reading cui vectors from %s" % (args[0]))
    cui_vecs = gensim.models.KeyedVectors.load(args[0])
    print("Reading word vectors from %s" % (args[1]))
    glove_vecs = gensim.models.KeyedVectors.load(args[1])

    print("Finding one-word terms in UMLS with CUIs in our cui vectors")
    cui_word_pairs = build_cuiword_pairs(args[2], cui_vecs, glove_vecs)
    align_size = len(cui_word_pairs)
    print('  Found %d pairs of cuis and words' % (len(cui_word_pairs)))

    ## Build reduced w2v matrices for computing the linear projection
    print("Filling reduced glove and cui matrices with %d rows" % (align_size))
    cui_matrix = np.zeros([align_size, cui_vecs.vector_size], dtype='float32')
    glove_matrix = np.zeros([align_size, glove_vecs.vector_size], dtype='float32')
    for row in range(align_size):
        cui_matrix[row,:] += cui_vecs[cui_word_pairs[row][0]]
        glove_matrix[row,:] += glove_vecs[cui_word_pairs[row][1]]
    
    ## Build full cui matrix for computing projections
    print("Building full cui matrix for computing projections")
    full_cui_matrix = torch.zeros([len(cui_vecs.vocab), cui_vecs.vector_size]).to(device)
    for row in range(len(cui_vecs.vocab)):
        cui = cui_vecs.index2word[row]
        full_cui_matrix[row,:] += torch.tensor(cui_vecs[cui]).to(device)

    cui_matrix = torch.tensor(cui_matrix).to(device)
    glove_matrix = torch.tensor(glove_matrix).to(device)

    projection = torch.zeros([cui_vecs.vector_size, glove_vecs.vector_size]).to(device)
    projection.normal_()
    projection.requires_grad_()

    loss = nn.MSELoss()
    optimizer = optim.SGD([projection], lr=1.0, weight_decay=0.01, momentum=0.9)
    
    for epoch in range(num_epochs+1):
        if epoch % 100 == 0:
            full_projection = torch.matmul(full_cui_matrix, projection).detach().cpu().numpy()
            for pair in example_pairs:
                cui, word = pair
                cui_vector = full_projection[ cui_vecs.vocab[cui].index ]
                word_vector = glove_vecs[word]
                sim = cos(cui_vector.reshape(1,-1), word_vector.reshape(1,-1))
                print("Similarity between %s and %s is %f" % (cui, word, sim))
        optimizer.zero_grad()
        similarity = torch.matmul(cui_matrix, projection) - glove_matrix
        epoch_loss = loss(similarity, torch.zeros_like(glove_matrix))
        epoch_loss.backward()
        optimizer.step()
        if epoch % 100 == 0:
            print("Loss in epoch %d is %f" % (epoch, epoch_loss))


    # Now project our GLOVE matrix with this learned projection and write as gensim 100d model
    print("Projecting full cui matrix into learned space")
    
    full_projection = torch.matmul(full_cui_matrix, projection).detach().cpu().numpy()

    print("Writing gensim file to %s" % (args[3]))
    tf = tempfile.NamedTemporaryFile(mode='wt')
    tf.write('%d %d\n' % (full_projection.shape[0], full_projection.shape[1]))
    for cui_ind in range(full_projection.shape[0]):
        cui = cui_vecs.index2word[cui_ind]
        vec = list(full_projection[cui_ind,:])
        str_vec = [str(x) for x in vec]
        tf.write('%s %s\n' % (cui, ' '.join(str_vec)))

    tf.seek(0)
    gs_new_vecs = gensim.models.KeyedVectors.load_word2vec_format(tf.name)
    gs_new_vecs.save(args[3])


if __name__ == '__main__':
    main(sys.argv[1:])

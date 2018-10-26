#!/usr/bin/env python3.6

from os.path import join, isfile
import sys
import glob
import re

import nltk
from nltk import pos_tag, word_tokenize

class Attribute:
    def __init__(self, cat, ent):
        self.cat = cat
        self.ent = ent

class Entity:
    def __init__(self, cat, start, end):
        self.cat = cat
        self.start = start
        self.end = end

brat_ent_patt = re.compile('^(T\d+)\s+(\S+) (\d+) (\d+)\s+(.+)$')
brat_att_patt = re.compile('^(A\d+)\s+(\S+) (T\d+).*$')

def read_brat_file(ann_fn):
    ents = {}
    atts = {}
    with open(ann_fn, 'r') as ann_file:
        line = ann_file.readline().rstrip()
        m = brat_att_patt.match(line)
        if not m is None:
            att_id = m.group(1)
            att_type = m.group(2)
            att_entid = m.group(3)
            atts[att_id] = Attribute(att_type, att_entid)
        else:
            m = brat_ent_patt.match(line)
            if not m is None:
                ent_id = m.group(1)
                ent_type = m.group(2)
                ent_start_ind = int(m.group(3))
                ent_end_ind = int(m.group(4))
                ent_text = m.group(5)
                ents[ent_id] = Entity(ent_type, ent_start_ind, ent_end_ind)
    return ents, atts


def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required argument: <chqa dir> <output directory>\n')
        sys.exit(-1)
    
    # get all .txt files from the chqa directory:
    txt_files = glob.glob(join(args[0], '*.txt'))
    for txt_fn in txt_files:
        ann_fn = txt_fn[:-3] + 'ann'
        if not isfile(ann_fn): continue

        print('Processing file %s which has corresponding file %s' % (txt_fn, ann_fn))

        with open(txt_fn, 'r') as myfile:
            text = myfile.read()
        
        ents, atts = read_brat_file(ann_fn)

        

                


if __name__ == '__main__':
    main(sys.argv[1:])

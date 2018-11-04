#!/usr/bin/env python3.6

from os.path import join, isfile
import sys
import glob
import re

import nltk
from nltk import pos_tag, word_tokenize

class Attribute:
    def __init__(self, cat, id):
        self.cat = cat
        self.id = id

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
        for line in ann_file.readlines():
            line = line.rstrip()
            m = brat_att_patt.match(line)
            if not m is None:
                att_id = m.group(1)
                att_type = m.group(2)
                att_entid = m.group(3)
                atts[att_entid] = Attribute(att_type, att_id)
            else:
                m = brat_ent_patt.match(line)
                if not m is None:
                    ent_id = m.group(1)
                    ent_type = m.group(2)
                    ent_start_ind = int(m.group(3))
                    ent_end_ind = int(m.group(4))
                    ent_text = m.group(5)
                    if ent_type == 'Focus' or ent_type == 'Coordination': 
                        continue
                    ents[ent_id] = Entity(ent_type, ent_start_ind, ent_end_ind)
        for ent_id in ents.keys():
            if ent_id in atts:
                ents[ent_id].cat += '-%s' % (atts[ent_id].cat)
    return ents, atts


def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required argument: <chqa dir> <output directory>\n')
        sys.exit(-1)
    
    # get all .txt files from the chqa directory:
    txt_files = glob.glob(join(args[0], '*.txt'))
    fout = open(join(args[1], 'qde.conll'), 'w')

    for txt_fn in txt_files:
        ann_fn = txt_fn[:-3] + 'ann'
        if not isfile(ann_fn): continue

        print('Processing file %s which has corresponding file %s' % (txt_fn, ann_fn))

        with open(txt_fn, 'r') as myfile:
            text = myfile.read()
        
        ents, atts = read_brat_file(ann_fn)
        tagged = pos_tag(word_tokenize(text))
        # section_starts = ()
        # section_ends = ()
        # section_names = ()
        awaited_starts = {}
        for ent_id in ents.keys():
            ent = ents[ent_id]
            # section_starts.append(ent.start)
            # section_ends.append(ent.end)
            name = ent.cat
            if ent_id in atts:
                name += '-%s' % (atts[ent_id].cat)
            # section_names.append(name)
            awaited_starts[ent.start] = ent_id

        start_ind = 0
        prev_label = 'O'
        awaited_ends = [] # list of (end_ind, label) pairs
        for tag in tagged:
            # tag[0] is the word and tag[1] is the POS
            token_start_ind = text.find(tag[0], start_ind)
            token_end_ind = token_start_ind + len(tag[0])
            start_ind = token_end_ind

            if len(awaited_ends) == 0 and len(awaited_starts) == 0:
                fout.write('%s\t%s\tO\n' % (tag[0], tag[1]))

            ## For BIO tagging, all active labels get printed as I
            for awaited in awaited_ends:
                fout.write('%s\t%s\tI-%s\n' % (tag[0], tag[1], awaited[1]))
            
            ## Remove entities that end on this token:
            new_awaited = []
            for awaited in awaited_ends:
                if awaited[0] != token_end_ind:
                    new_awaited.append(awaited)
            awaited_ends = new_awaited

            ## All awaited starts get printed as B 
            if token_start_ind in awaited_starts:
                ent_id = awaited_starts[token_start_ind]
                ent = ents[ent_id]
                fout.write('%s\t%s\tB-%s\n' % (tag[0], tag[1], ent.cat))

                awaited_starts.pop(token_start_ind)
                awaited_ends.append( (ent.end, ent.cat) )
        # break
        fout.write('\n')
    fout.close()





        

                


if __name__ == '__main__':
    main(sys.argv[1:])

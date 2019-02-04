#!/usr/bin/env python3.6

from os.path import join, isfile, basename
import sys
import glob
import re

import nltk
from nltk import pos_tag, word_tokenize
from ctakes_rest import get_cui_maps

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
                if not att_entid in atts:
                    # print(f'Annotation file {ann_fn} has two attributes with the same entity id {att_entid}')
                    # print(f'  Existing one is {atts[att_entid].cat} and new one is {att_type}')
                    atts[att_entid] = []
                atts[att_entid].append(Attribute(att_type, att_id))
            else:
                m = brat_ent_patt.match(line)
                if not m is None:
                    ent_id = m.group(1)
                    ent_type = m.group(2)
                    ent_start_ind = int(m.group(3))
                    ent_end_ind = int(m.group(4))
                    ent_text = m.group(5)
                    ## The following are not sentence-level annotations so may overlap:
                    if ent_type == 'Focus' or ent_type == 'Coordination' or ent_type == 'Exemplification': 
                        continue
                    ents[ent_id] = Entity(ent_type, ent_start_ind, ent_end_ind)
    return ents, atts


def main(args):
    if len(args) < 3:
        sys.stderr.write('Two required argument: <chqa dir> <conll-format output directory> <flair-format output directory>\n')
        sys.exit(-1)
    
    labels = ('Comorbidity', 'DiagnosisAtt', 'Family_History', 'ISF', 'LifeStyle', 'Symptom', 'TestAtt', 'TreatmentAtt')

    # get all .txt files from the chqa directory:
    txt_files = glob.glob(join(args[0], '*.txt'))
    fout = open(join(args[1], 'qde.conll'), 'w')
    flair_out = open(join(args[2], 'sentences.flair'), 'w')
    # Create a map from labels to the file pointer for the file for that label:
    bg_out = {label:open(join(args[2], f'bg-{label.lower()}.flair'), 'w') for label in labels}

    for txt_fn in txt_files:
        fn_prefix = txt_fn[:-4]
        ann_fn = fn_prefix + '.ann'
        if not isfile(ann_fn): continue

        print('Processing file %s which has corresponding file %s' % (txt_fn, ann_fn))

        with open(txt_fn, 'r') as myfile:
            text = myfile.read()
        
        ents, atts = read_brat_file(ann_fn)

        tagged = pos_tag(word_tokenize(text))
        cui_start_map, cui_end_map = get_cui_maps(text)
        
        awaited_starts = {}
        for ent_id in ents.keys():
            ent = ents[ent_id]

            ## Write to Flair format:
            flair_out.write('__label__%s %s\n' % (ent.cat.lower(), text[ent.start:ent.end]))
            
            ## write BG sentences to flair format:
            if ent.cat.lower() == 'background':
                labels = {label:False for label in labels}
                if ent_id in atts:
                    for att in atts[ent_id]:
                        labels[att.cat] = True
                
                for label in labels:
                    bg_out[label].write('__label__%s %s\n' % (labels[label], text[ent.start:ent.end]))

            ## Prepare for writing conll format
            awaited_starts[ent.start] = ent_id

        start_ind = 0
        prev_label = 'O'
        prev_cui_label = 'O'
        cur_cui_end = -1
        awaited_ends = [] # list of (end_ind, label) pairs
        for tag in tagged:
            # tag[0] is the word and tag[1] is the POS
            token_start_ind = text.find(tag[0], start_ind)
            token_end_ind = token_start_ind + len(tag[0])
            start_ind = token_end_ind

            cui_label = 'O'
            if token_start_ind in cui_start_map:
                # New cui label no matter what the old one was:
                cui_label = cui_start_map[token_start_ind][0]
                cur_cui_end = cui_start_map[token_start_ind][1]
            elif cur_cui_end > token_end_ind:
                # This is a special case for where tokenization differs between python and ctakes and
                # cui borders don't align with word borders
                cui_label = 'O'
                cur_cui_end = -1
            elif not prev_cui_label == 'O':
                cui_label = prev_cui_label

            if len(awaited_ends) == 0 and len(awaited_starts) == 0:
                fout.write('%s\t%s\t%s\tO\n' % (tag[0], tag[1], cui_label))

            ## For BIO tagging, all active labels get printed as I
            for awaited in awaited_ends:
                fout.write('%s\t%s\t%s\tI-%s\n' % (tag[0], tag[1], cui_label, awaited[1]))
            
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
                fout.write('%s\t%s\t%s\tB-%s\n' % (tag[0], tag[1], cui_label, ent.cat))

                awaited_starts.pop(token_start_ind)
                awaited_ends.append( (ent.end, ent.cat) )
            
            if token_end_ind in cui_end_map:
                cui_label = 'O'
            
            prev_cui_label = cui_label

        # break
        fout.write('\n')
    fout.close()
    flair_out.close()
    [fp.close() for fp in bg_out.values()]


if __name__ == '__main__':
    main(sys.argv[1:])

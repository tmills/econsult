
from brat import read_brat_file
import glob
import numpy as np
from os.path import join, isfile, exists
import os
import sys

from ctakes_rest import get_cui_maps

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required argument: <chqa dir> <flair-format output directory>\n')
        sys.exit(-1)
    
    labels = ('Comorbidity', 'DiagnosisAtt', 'Family_History', 'ISF', 'LifeStyle', 'Symptom', 'TestAtt', 'TreatmentAtt')

    # get all .txt files from the chqa directory:
    txt_files = glob.glob(join(args[0], '*.txt'))
    flair_out = open(join(args[1], 'mixed-sentences.flair'), 'w')
    out_dir = join(args[1], 'mixed-bg')
    if not exists(out_dir):
        os.makedirs(out_dir)
    train_out = open(join(out_dir, 'train.txt'), 'w')
    dev_out = open(join(out_dir, 'dev.txt'), 'w')
    test_out = open(join(out_dir, 'test.txt'), 'w')

    for txt_fn in txt_files:
        fn_prefix = txt_fn[:-4]
        ann_fn = fn_prefix + '.ann'
        if not isfile(ann_fn): continue

        print('Processing file %s which has corresponding file %s' % (txt_fn, ann_fn))

        last_number = int(fn_prefix[-1])
        if last_number % 8 == 0:
            fout = dev_out
        elif last_number % 6 == 0 or last_number % 7 == 0:
            fout = test_out
        else:
            fout = train_out

        with open(txt_fn, 'r') as myfile:
            text = myfile.read()
        
        ents, atts = read_brat_file(ann_fn)

        for ent_id in ents.keys():
            ent = ents[ent_id]
            ent_text = text[ent.start:ent.end]

            # get cuis for this entity:
            cui_start_map, cui_end_map = get_cui_maps(ent_text)
            cui_starts_reversed = list(np.sort(list(cui_start_map.keys())))
            cui_starts_reversed.reverse()

            # Replace text with cuis
            for cui_start in cui_starts_reversed:
                (cui, cui_end) = cui_start_map[cui_start]
                ent_text = ent_text[:cui_start] + cui + ent_text[cui_end:]
                # ent_text[cui_start:cui_end] = cui

            ## Write to Flair format:
            line = '__label__%s %s\n' % (ent.cat.lower(), ent_text)
            fout.write(line)
            flair_out.write(line)

if __name__ == '__main__':
    main(sys.argv[1:])

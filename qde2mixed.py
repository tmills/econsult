
from brat import read_brat_file
import glob
import numpy as np
from os.path import join, isfile, exists
import os
import sys

from ctakes_rest import get_mixed_sent

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required argument: <chqa dir> <flair-format output directory>\n')
        sys.exit(-1)
    
    attributes = ('Comorbidity', 'DiagnosisAtt', 'Family_History', 'ISF', 'LifeStyle', 'Symptom', 'TestAtt', 'TreatmentAtt')

    # get all .txt files from the chqa directory:
    txt_files = glob.glob(join(args[0], '*.txt'))
    flair_out = open(join(args[1], 'mixed-sentences.flair'), 'w')
    bg_out = open(join(args[1], 'mixed-bg.flair'), 'w')
    out_dir = join(args[1], 'mixed-sentences')
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

            mixed_sent = get_mixed_sent(ent_text)
            
            ## Write to Flair format:
            line = '__label__%s %s\n' % (ent.cat.lower(), mixed_sent)
            fout.write(line)
            flair_out.write(line)

            ## write BG sentences to flair format:
            if ent.cat.lower() == 'background':
                labels = {label:False for label in attributes}
                if ent_id in atts:
                    for att in atts[ent_id]:
                        labels[att.cat] = True
                
                for label in attributes:
                    if labels[label]:
                        bg_out.write('__label__%s ' % (label))
                
                bg_out.write('%s\n' % (mixed_sent))

if __name__ == '__main__':
    main(sys.argv[1:])

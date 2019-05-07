#!/usr/bin/env python

import argparse
import json
from os.path import join
import sys

parser = argparse.ArgumentParser(description='Preprocessor for medical NLI task data')
parser.add_argument('mnli_dir', help="Directory where mnli data is stored")
parser.add_argument('out_dir', help="Directory to write out Flair-formatted data")
parser.add_argument('-c', '--cuis', action="store_true", default=False)

def main(args):
    args = parser.parse_args(args)

    for partition in ('train', 'dev', 'test'):
        in_file = join(args.mnli_dir, 'mli_%s_v1.jsonl' % partition)
        out_file = join(args.out_dir, '%s.txt' % partition)

        with open(in_file) as fp:
            with open(out_file, 'w') as out:
                for line in fp.readlines():
                    obj = json.loads(line)
                    cat = obj['gold_label']
                    sent1 = obj['sentence1']
                    sent2 = obj['sentence2']

                    if args.cuis:
                        print("Not implemented yet!")
                        return

                    out_line = '__label__%s %s %s\n' % (cat, sent1, sent2)
                    out.write(out_line)


if __name__ == '__main__':
    main(sys.argv[1:])

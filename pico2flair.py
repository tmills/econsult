
from os.path import join, exists
import os
import sys


def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required argument: <pico dir> <flair-format output directory> \n')
        sys.exit(-1)

    splits = ['dev', 'test', 'train']
    for split in splits:
        # Create output files for each split:
        std_out_dir = join(args[1], 'std')
        if not exists(std_out_dir):
            os.makedirs(std_out_dir)
        std_out_file = join(std_out_dir, '%s.txt' % (split))
        sof = open(std_out_file, 'wt')

        mixed_out_dir = join(args[1], 'mixed')
        if not exists(mixed_out_dir):
            os.makedirs(mixed_out_dir)
        mixed_out_file = join(mixed_out_dir, '%s.txt' % (split))
        mof = open(mixed_out_file, 'wt')


        in_file = join(args[0], 'PICO_%s.txt' % (split))
        with open(in_file, 'r') as in_f:
            for line in in_f:
                line = line.rstrip()
                if line == '' or line[0] == '#':
                    continue

                header, label, sent = line.split('|')

                sof.write('__label__%s %s\n' %(label, sent) )

        sof.close()
        mof.close()
                    


if __name__ == '__main__':
    main(sys.argv[1:])

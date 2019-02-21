from ctakes_rest import get_cui_maps

import numpy as np
import sys

def main(args):
    if len(args) < 1:
        sys.stderr.write('Two required arguments: <input file>\n')
        sys.exit(-1)

    with open(args[0], 'r') as in_file:
        for line in in_file.readlines():
            sent = line.rstrip()
    
            # get cuis for this entity:
            cui_start_map, cui_end_map = get_cui_maps(sent)
            cui_starts_reversed = list(np.sort(list(cui_start_map.keys())))
            cui_starts_reversed.reverse()

            # Replace text with cuis
            for cui_start in cui_starts_reversed:
                (cui, cui_end) = cui_start_map[cui_start]
                sent = sent[:cui_start] + cui + sent[cui_end:]
            print(sent)
 
if __name__ == '__main__':
    main(sys.argv[1:])


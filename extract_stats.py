import sys
from collections import Counter

def main(args):
    if len(args) < 2:
        sys.stderr.write('2 required argument: <cuis file> <mrconso path>\n')
        sys.exit(-1)

    print("Reading CUI preferred terms from MRCONSO file")
    cui_dict = {}
    with open(args[1], 'r') as mrc:
        for line in mrc.readlines():
            fields = line.split('|')
            cui, preferred_term = fields[0], fields[14]
            if not cui in cui_dict:
                cui_dict[cui] = preferred_term

    print("Building cui-count maps for each semantic type")
    sem_types = {}
    sem_type_counts = {}
    with open(args[0], 'rt') as f:
        for line in f.readlines():
            sem_type, cui, _, count = line.rstrip().split(' ')
            if not sem_type in sem_types:
                sem_types[sem_type] = {}
                sem_type_counts[sem_type] = 0

            sem_types[sem_type][cui] = int(count)
            sem_type_counts[sem_type] += int(count)

    for sem_type in sem_types.keys():
        print("**** Semantic type : %s" % (sem_type))
        cui_counts = Counter( sem_types[sem_type] )
        for cui,count in cui_counts.most_common(20):
            preferred_term = "Not found"
            if cui in cui_dict:
                preferred_term = cui_dict[cui]
            print("%s (%s) => %d (%f)" % (preferred_term, cui, count, count / sem_type_counts[sem_type]))

if __name__ == '__main__':
    main(sys.argv[1:])

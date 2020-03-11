#!/usr/bin/env python

from pattern.en import spelling
import sys

def main(args):
    if len(args) < 1:
        sys.stderr.write("1 required argument: <input file>")
    

    with open(args[0], 'r') as f:
        for line in f.readlines():
            word = line.rstrip()
            try:
                suggestions = spelling.suggest(word)
            except:
                suggestions = "No suggestions"
            print('%s %s' % (word, str(suggestions)))

if __name__ == '__main__':
    main(sys.argv[1:])
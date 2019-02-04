#!/usr/bin/env python3.7

from os.path import join
import sys

import nltk
from nltk import pos_tag, word_tokenize
from ctakes_rest import get_cui_maps

def main(args):
    if len(args) < 2:
        sys.stderr.write('Two required argument: <chqa file> <output directory>\n')
        sys.exit(-1)
    
    focus_out = open(join(args[1], 'focus.conll'), 'w')
    qt_out = open(join(args[1], 'qt.flair'), 'w')

    import xml.etree.ElementTree as ET
    tree = ET.parse(args[0])
    root = tree.getroot()

    for request in root.findall('Request'):
        text = request.find('Text').text
        tagged = pos_tag(word_tokenize(text))
        cui_start_map, cui_end_map = get_cui_maps(text)

        focus = request.find('Focus')
        if not focus is None:
            focus_start = int(focus.attrib['start'])
            focus_end = int(focus.attrib['len']) + focus_start
            # print("Focus is: %s" % ( text[focus_start:focus_end] ) )
        
        start_ind = 0
        prev_label = 'O'
        prev_cui_label = 'O'
        cur_cui_end = -1
        for tag in tagged:
            # tag[0] is the word and tag[1] is the POS
            token_start_ind = text.find(tag[0], start_ind)
            token_end_ind = token_start_ind + len(tag[0])
            start_ind = token_end_ind
            if focus_start == token_start_ind:
                label = 'B-FOCUS'
            elif (prev_label == 'B-FOCUS' or prev_label == 'I-FOCUS') and token_end_ind <= focus_end:
                label = 'I-FOCUS'
            else:
                label = 'O'

            cui_label = 'O'
            if token_start_ind in cui_start_map:
                cui_label = cui_start_map[token_start_ind][0]
                cur_cui_end = cui_start_map[token_start_ind][1]
            elif cur_cui_end > token_end_ind:
                # This is a special case for where tokenization differs between python and ctakes and
                # cui borders don't align with word borders
                cui_label = 'O'
            elif not prev_cui_label == 'O':
                cui_label = prev_cui_label

            focus_out.write('%s\t%s\t%s\t%s\n' % (tag[0], tag[1], cui_label, label) )

            if token_end_ind in cui_end_map:
                cui_label = 'O'

            prev_label = label
            prev_cui_label = cui_label

        for question in request.findall('Question'):
            qid = question.attrib['id']
            q_start = int(question.attrib['start'])
            q_end = int(question.attrib['len']) + q_start
            q_text = text[q_start:q_end]
            for sub_q in question.findall('SubQuestion'):
                q_cat = sub_q.attrib['qt']

                # print('Question \'%s\' has type %s' % (q_text, q_cat))

        focus_out.write('\n')
    focus_out.close()
    qt_out.close()

if __name__ == '__main__':
    main(sys.argv[1:])

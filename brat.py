import re

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

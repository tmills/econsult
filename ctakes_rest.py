#!/usr/bin/env python3.6

import requests

def add_cuis(json, sem_type, cui_list):
    for atts in json[sem_type]:
        begin = atts['begin']
        end = atts['end']
        polarity = atts['polarity']
        for cuiAtts in atts['conceptAttributes']:
            cui_list.append( (cuiAtts['cui'], begin, end) )
   
    return cui_list

def get_cuis(json):
    cuis = []

    cuis = add_cuis(json, 'DiseaseDisorderMention', cuis)
    cuis = add_cuis(json, 'SignSymptomMention', cuis)
    cuis = add_cuis(json, 'AnatomicalSiteMention', cuis)
    cuis = add_cuis(json, 'MedicationMention', cuis)
    cuis = add_cuis(json, 'ProcedureMention', cuis)

    return cuis

def process_sentence(sent):
    url = 'http://localhost:8080/ctakes-web-rest/service/analyze'
    r = requests.post(url, data=sent.encode('utf-8'))
    return get_cuis(r.json())

def get_cui_maps(sent):
    cuis = process_sentence(sent)
    cui_start_map = {}
    cui_end_map = {}
    for cui,begin,end in cuis:
        if begin in cui_start_map:
            # Collision: if existing cui with this begin ends later (is longer), skip this cui
            collision_end = cui_start_map[begin][1]
            if collision_end > end:
                break
            else:
                # new cui is longer span than old one, so remove the old end from the end map
                cui_end_map.pop(collision_end, None)

        if end in cui_end_map:
            # Collision: if existing cui with this end begins earlier (is longer), skip this cui
            collision_begin = cui_end_map[end][1]
            if collision_begin < begin:
                break
            else:
                # new cui is longer span than old one, so remove the old begin from the start map
                cui_start_map.pop(collision_begin, None)
        
        # If we get this far then our cui has no collision or is longer than existing spans it collides with.
        cui_start_map[begin] = (cui, end)
        cui_end_map[end] = (cui, begin)

    return cui_start_map, cui_end_map

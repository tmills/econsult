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
    url = 'http://tmill-desktop:8080/ctakes-web-rest/service/analyze'
    r = requests.post(url, data=sent.encode('utf-8'))
    return get_cuis(r.json())

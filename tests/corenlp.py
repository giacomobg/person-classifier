"""Test CoreNLP's NER on entities and persons in my database."""
# add parent directory to sys.path
import os
import sys
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.split(os.path.abspath(dir_path))[0])

import traceback, requests,time
from libraries.create_model import Modeller

def stanford_ner(string):
    """Send request to CoreNLP server for name entity recognition."""
    corenlp_url = 'http://localhost:9000'
    string = string.encode(encoding='utf-8')
    params = {
        'properties': '{"annotators": "ner", "outputFormat": "json"}'
    }
    try:
        r = requests.post(url=corenlp_url,params=params, data=string)
        json = r.json()
        # Store Name entity Recognition data in self.ner.
        ner = json['sentences'][0]['tokens']
    except:
        print('CoreNLP Name Entity Recognition failed.')
        traceback.print_exc()
        ner = []
    string = string.decode(encoding='utf-8')
    return ner

def corenlp():
    """Test corenlp's ner against the database"""
    # limit should be the int of sentences to extract from database or 'all' to extract all
    limit='all'
    modeller = Modeller()
    modeller.get_wiki_data(limit=limit)
    strings,y_vals = zip(*modeller.data)
    print('Total strings:',len(y_vals))
    print('People:',sum(y_vals))
    print('Other entities:',len(y_vals) - sum(y_vals))

    correct_person = 0
    correct_non_person = 0
    false_positive = 0
    false_negative = 0

    print('\nPutting strings through CoreNLP')
    start_time_corenlp = time.time()
    for counter,(string,y) in enumerate(modeller.data):
        # pass string to stanford ner
        ner = stanford_ner(string)
        # check if ner indicates there is a person in the string
        person = False
        for word in ner:
            if word['ner'] == 'PERSON':
                person = True
                break
        if person:
            if y:
                correct_person += 1
            else:
                false_positive += 1
        else:
            if y:
                false_negative += 1
            else:
                correct_non_person += 1
    print('Strings put through CoreNLP in:',round(time.time()-start_time_corenlp),'seconds')


    precision = correct_person/(correct_person+false_positive)
    recall = correct_person/(correct_person+false_negative)
    f1_score = 2*(precision*recall)/(precision+recall)
    print('Precision:',round(precision,2),'\nRecall:',round(recall,2),'\nF1 score:',round(f1_score,2))
    # compute precision, recall, f1_score

if __name__ == '__main__':
	corenlp()

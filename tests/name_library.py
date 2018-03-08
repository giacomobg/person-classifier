"""Test a system that searches for first names at the start of a string
and surnames at the end of a string in order to decide whether it is a person.
"""
# add parent directory to sys.path
import os
import sys
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.split(os.path.abspath(dir_path))[0])

import traceback, requests, time
import pandas as pd
from libraries.create_model import Modeller

def name_library(limit):
    """Use a library of US surnames from
    http://www2.census.gov/topics/genealogy/2000surnames/names.zip
    and UK first names from
    https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/babynamesenglandandwalesbabynamesstatisticsboys/2016/adhocallbabynames1996to2016.xls
    to check if entries in entities.db are people.
    """
    modeller = Modeller(limit=limit)
    modeller.get_wiki_data()
    strings,y_vals = zip(*modeller.data)
    print('Total strings:',len(y_vals))
    print('People:',sum(y_vals))
    print('Other entities:',len(y_vals) - sum(y_vals))

    correct_person = 0
    correct_non_person = 0
    false_positive = 0
    false_negative = 0

    print('\nChecking if strings are people')
    start_time = time.time()
    with open('libraries/data/app_c.csv') as csv_file:
        df = pd.read_csv(csv_file)
    surnames = df.name.unique()
    with open('libraries/data/first_names_uk.csv') as csv_file:
        df = pd.read_csv(csv_file,header=None,names=['name'])
    firstnames = df.name.unique()

    for counter,(string,y) in enumerate(modeller.data):
        person = False
        possbl_fn = string.split(' ')[0].upper()
        possbl_fn += ' ' # for some reason the dataset has a space after each name
        possbl_sn = string.split(' ')[-1].upper()
        # print(possbl_fn)
        # print(possbl_fn in firstnames)
        if possbl_fn in firstnames:
            person = True
        if possbl_sn in surnames:
            person = True
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
    print('Strings checked in:',round(time.time()-start_time),'seconds')


    precision = correct_person/(correct_person+false_positive)
    recall = correct_person/(correct_person+false_negative)
    f1_score = 2*(precision*recall)/(precision+recall)
    print('Precision:',round(precision,2),'\nRecall:',round(recall,2),'\nF1 score:',round(f1_score,2))
    # compute precision, recall, f1_score

if __name__ == '__main__':
    # limit is number of entries to retrieve from database.
    # either an int or 'all' to retrieve all.
    name_library(limit='all')
import time,sqlite3,pickle,requests
import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier


class Modeller():
    """Manipulates data, builds and saves an ML model trained to decide
    whether a string is a name of a person.

    args:
    limit --- either int or 'all' - number of entries to retrieve from database.
                                    if set to all, all entries are retrieved.
    """

    def __init__(self,limit):
        self.feature_names = [
            'first_letter_uppercase',
            'all_words_uppercase',
            'all_letters_uppercase',
            'length',
            'contains_digit',
            'all_digits',
            'num_words',
            'first_word_length',
            'last_word_length',
            'last_word_upper',
            'freq_firstname',
            'freq_surname'
            ]
        self.num_numerical_features = len(self.feature_names)

        # open surname file
        with open('libraries/data/app_c.csv') as csv_file:
            self.surnames = pd.read_csv(csv_file)
        self.surnames = self.surnames[['name','count']]
        self.surname_list = self.surnames.name.unique()
        # open first name file
        with open('libraries/data/first_names_uk.csv') as csv_file:
            self.firstnames = pd.read_csv(csv_file)
        self.firstnames = self.firstnames[['name','count']]
        self.firstname_list = self.firstnames.name.unique()
        self.limit = limit

    def get_wiki_data(self):
        """ Get data from entities.db """
        self.db = sqlite3.connect('libraries/data/entities.db')
        self.cursor = self.db.cursor()
        print('Retrieving data from db')
        start_time_db = time.time()
        if self.limit == 'all':
            self.cursor.execute("SELECT * FROM entities;") # limit reduces size of dataset for prototyping
        else:
            self.limit = (self.limit,)
            self.cursor.execute("SELECT * FROM entities LIMIT ? ;",self.limit) # limit reduces size of dataset for prototyping
        self.data = self.cursor.fetchall()
        print('Retrieved data from db in',round(time.time() - start_time_db),'seconds')
        # split data into its columns, name and person
        # strings,y_vals = zip(*self.data)
        # print('People:',sum(y_vals))
        # print('Other entities:',len(y_vals) - sum(y_vals))
        self.train,self.test = train_test_split(self.data,test_size=0.2)
        self.str_train,self.y_train = zip(*self.train)
        self.str_test,self.y_test = zip(*self.test)


    def freq_firstname(self,string):
        """Returns frequency of first word as a first name.
        
        string -- contains solely the first name.
        """
        word = string.upper()
        # check if first name is in the list
        if word not in self.firstname_list:
            return 0
        else:
            return self.firstnames.loc[self.firstnames.name == word,['count']].values[0][0]

    def freq_surname(self,string):
        """Returns frequency of last word as a surname.
        
        string -- contains solely the surname.
        """
        word = string.upper()
        # check if surname is in the list
        if word not in self.surname_list:
            return 0
        else:
            return self.surnames.loc[self.surnames.name == word,['count']].values[0][0]

    def str2features(self,string):
        """Take input string and return list of features."""
        str_as_lst = string.split(' ')
        # remove empty strings from str_as_lst
        str_as_lst = [i for i in str_as_lst if i != '']

        # compute last word length feature
        if len(str_as_lst) == 1:
            len_last_word = 0
        else:
            len_last_word = len(str_as_lst[-1])

        features = [
            string[0].isupper(),
            string.istitle(),
            string.isupper(),
            len(string),
            any(char.isdigit() for char in string),
            string.isdigit(),
            len(str_as_lst),
            len(str_as_lst[0]),
            len_last_word,
            str_as_lst[-1][0].isupper(),
            self.freq_firstname(str_as_lst[0]),
            self.freq_surname(str_as_lst[-1])
            ]

        return features

    def feature_extraction(self,strings):
        """Execute feature extraction

        strings -- list of input strings
        a -- np array of features
        """
        print('Executing feature extraction')
        start_time_ftr_extr = time.time()
        a = np.zeros([len(strings),self.num_numerical_features])
        for counter,s in enumerate(strings):
            if s == ' ':
                continue
            features = self.str2features(s)
            a[counter,:] = features
        self.length = a.shape[0]
        print('Feature extraction executed in',round(time.time() - start_time_ftr_extr),'seconds')
        return a


    def create_model(self):
        """Build model, self.clf"""
        self.clf = tree.DecisionTreeClassifier()
        # self.clf = RandomForestClassifier()
        # self.clf = sklearn.svm.SVC()
        print('Training model')
        start_time_training = time.time()
        self.clf.fit(self.x_train,self.y_train)
        print('Trained model in',round(time.time() - start_time_training),'seconds')
        # print(np.round(self.clf.coef_,1))
        print('\nFeature importance:\n'self.clf.feature_importances_)

    def model_evaluation(self):
        """ Use test dataset to test model"""
        y_pred = self.clf.predict(self.x_test)
        print('F1 score:        ',round(sklearn.metrics.f1_score(self.y_test,y_pred),2))
        print('Person precision:',round(sklearn.metrics.precision_score(self.y_test,y_pred),2))
        print('Person recall:   ',round(sklearn.metrics.recall_score(self.y_test,y_pred),2))

    def pickle_model(self):
        with open('libraries/obj/model.pkl','wb') as out:
            pickle.dump(self.clf,out)
        print('Model pickled.')


    def wrapper(self):
        """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ~~~~~~~~~~~~~~~~~~MAIN FUNCTION~~~~~~~~~~~~~~~~~~~~
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
        self.get_wiki_data()
        self.x_train = self.feature_extraction(self.str_train)
        self.x_test = self.feature_extraction(self.str_test)
        self.create_model()
        self.model_evaluation()
        self.pickle_model()


    def load_model(self):
        """Unpickle existing ML model."""
        with open('libraries/obj/model.pkl','rb') as file:
            self.loaded_clf = pickle.load(file)
        print('Model loaded.')

    def interface(self):
        """Command line interface for querying model with strings"""
        while True:
            query = input('Type query or quit:\n')
            if query == 'quit':
                break
            feature_array = self.feature_extraction([query])
            pred = self.loaded_clf.predict(feature_array)
            if pred == 0:
                print('N - Not a person')
            elif pred == 1:
                print('Y - Is a person')

    def query_model(self):
        """Wrapper for functions required to querying existing model"""
        self.load_model()
        self.interface()
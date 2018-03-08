# Person Classifier

Builds a decision tree that identifies strings that represent names of people.

Run in Python 3.


### Data preparation

Download the following .ttl file from dbpedia:

http://downloads.dbpedia.org/2016-10/core-i18n/en/instance_types_transitive_en.ttl.bz2

Run `ttl2db.py` to extract relevant data and store it in an sqlite3 database at `libraries/data/entities.db`.
The database has one table with two columns, `name` and `person`. The former is a string, person is 0 or 1 and indicates whether it is a person.
Since steps were taken to avoid loading the entire .ttl into memory, this can take 3 hours!


### Model training

Run `model_me.py` to build a decision tree that is pickled and saved to `libraries/obj/model.pkl`.

Features used:
* Is the first letter uppercase?
* Are the first letters of all the words uppercase?
* Are all the letters uppercase?
* How many characters are in the string?
* Does the string contain a digit?
* Is the string solely digits?
* How many words are in the string?
* How long is the first word?
* How long is the last word?
* Is the first word a UK first name? If so, how many UK babies in the last 20 years were given that name?
* IS the last word a US surname? If so, what is its frequency in the US?
Details on name lists below.


### Try out the model

Run `query_me.py` to pass the model queries i.e. ask it to classify strings. Queries are typed out at the command line.
This works immediately since a ready built model at `libraries/obj/model.pkl` is in the repository.


### How good is it?

In order to get a frame of reference, there are two files that use other methods. The tree has a higher F1 score than both of these.

###### CoreNLP
Set up a CoreNLP server at localhost:9000. Documentation is found at:

https://stanfordnlp.github.io/CoreNLP/corenlp-server.html

Run `tests/corenlp.py`. Evaluates the CoreNLP NER at the task.

###### Name libraries
Run `tests/name_library.py`.
This checks if the first word in the string is in `libraries/data/first_names_uk.csv`, a file created from ONS data at

https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/babynamesenglandandwalesbabynamesstatisticsboys/2016/adhocallbabynames1996to2016.xls

and checks if the last word in the string is in `libraries/data/app_c.csv`, a list of US surnames in the Census 2000 found at

http://www2.census.gov/topics/genealogy/2000surnames/names.zip

###### F1 scores

|           |My model  |CoreNLP  |Name libraries|
|-----------|----------|---------|--------------|
|Precision  |**0.81**  |0.67     |0.63          |
|Recall     |**0.83**  |0.97     |0.78          |
|F1         |**0.82**  |0.79     |0.70          |


### Further work

* Add random strings and dictionary words to the sqlite3 database. Right now the model is being trained to tell between *people* and *other entities*. Then again, it depends on the purpose of the tool.

* Feature selection. Some features are not independent of one another, so perhaps some are redundant.

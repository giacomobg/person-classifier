import rdflib
from rdflib.namespace import FOAF
import sqlite3,time,re

class Process():
    """docstring for Process"""
    def __init__(self):
        super(Process, self).__init__()
        
    def connect_to_db(self):
        """ Connect to sqlite3 db and remove existing rows"""
        self.db = sqlite3.connect('libraries/data/entities.db')
        # Remove existing rows from db
        self.cursor = self.db.cursor()
        # delete table if it exists
        self.cursor.execute('''DROP TABLE IF EXISTS entities;''')
        # create table
        self.cursor.execute('''
                                CREATE TABLE entities (
                                    name text,
                                    person integer
                                );
                            ''')
        self.db.commit()

    def insert_into_db(self):
        """ Insert entity information into sqlite3 db"""
        print('Putting information into database')
        start_time_db = time.time()
        cursor = self.db.cursor()
        cursor.executemany('''
            INSERT INTO entities(name, person)
            VALUES(:name, :person)
            ''', self.entities)
        self.db.commit()
        print('Done in',round(time.time() - start_time_db),'seconds')
        self.entities = []

    def file_to_db(self):
        """ Create generator for iterating over lines in dbpedia source."""
        self.entities = []
        with open('instance_types_transitive_en.ttl') as file:
            start_time = time.time()
            for counter,line in enumerate(file):
                # if time.time() - start_time > 5:
                    # break
                if counter % 500000 == 0:
                    print(counter,'lines after',round(time.time() - start_time),'seconds')
                entity = self.parse_line(line)
                if entity is not None:
                    self.entities.append(entity)
                # Insert self.entities into db and delete its contents. If it becomes too big it might become a strain on the computer.
                if counter % 1000000 == 0:
                    self.insert_into_db()
            self.insert_into_db()
        print(round(time.time() - start_time),'seconds')

    def parse_line(self,line):
        """ Parse line of turtle file.
        line is a string.
        """
        g = rdflib.Graph()
        ontology = rdflib.Namespace("http://schema.org/")#dbpedia.org/ontology/")
        entity = {}

        g.parse(data=line, format="turtle")
        for triple in g.triples((None,None,None)):
            parsed_uri = g.compute_qname(uri=triple[2])
            if ontology == parsed_uri[1]:
                # entity_type 1 is Person, 0 is other
                tmp = False
                if parsed_uri[2] == 'Person':
                    entity['person'] = 1
                else:
                    entity['person'] = 0

                try:
                    # TODO: what about names with sports teams in?
                    name = g.compute_qname(uri=triple[0])[2]
                except:
                    # Exception caught if URI contains a bracket or other disallowed char e.g. http://dbpedia.org/resource/Honorius_(emperor)
                    continue
                    tmp = True
                if tmp:
                    print(tmp)
                # ignore empty strings
                # Replace underscores with spaces
                name = name.replace('_',' ')
                # remove '  1' from end of name if present
                pattern = re.compile("  [0-9]")
                if pattern.match(name[-3:]):
                    name = name[:-3]
                if name == '':
                    print(triple)
                    print(g.compute_qname(uri=triple[0])[2])
                    continue
                if name[0] == ' ':
                    name = name[1:]
                entity['name'] = name
                return entity

    def remove_duplicates_db(self):
        # Remove duplicates from the database.
        print('Removing duplicates')
        start_time_dupl = time.time()
        self.cursor.execute('''DELETE FROM entities
                                WHERE rowid NOT IN
                                (SELECT min(rowid) FROM entities GROUP BY name,person)''')
        # If a person is in the database twice as both a person and not a person, remove entry where it is not a person.
        self.cursor.execute('''DELETE FROM entities
                                WHERE person = 0
                                AND name IN
                                (SELECT name FROM entities WHERE person = 1)''')
        self.db.commit()
        print('Removed duplicates in',round(time.time() - start_time_dupl),'seconds')

    def wrapper(self):
        self.connect_to_db()
        self.file_to_db()
        self.remove_duplicates_db()
        self.db.close()


if __name__ == "__main__":
    process = Process()
    process.wrapper()
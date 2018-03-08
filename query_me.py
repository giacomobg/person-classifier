from create_model import Modeller

def query_me():
    """Query the most recently saved model.
    User is prompted at the command line for
    a query after running the file.
    """
    modeller = Modeller(limit='all')
    modeller.query_model()

if __name__ == '__main__':
    query_me()
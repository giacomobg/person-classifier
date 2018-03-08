from create_model import Modeller

def model_me():
    """Build and save ml model predicting
    whether or not a string is a name.
    """
    modeller = Modeller(limit='all')
    modeller.wrapper()

if __name__ == '__main__':
    model_me()
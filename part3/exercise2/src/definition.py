

class Definition:
    def __init__(self, rawText=None, preprocessed=None):
        self.__raw = rawText
        self.__preprocessed = preprocessed

    def get_raw(self):
        return self.__raw

    def set_raw(self, rawText):
        self.__raw = rawText

    def get_preprocessed(self):
        return self.__preprocessed
    
    #list of preprocessed text
    def set_preprocessed(self, preprocessed):
        self.__preprocessed = preprocessed

    def __str__(self):
        return '\t'.join(('{} = {}'.format(item[15:], self.__dict__[str(item)]) for item in self.__dict__))

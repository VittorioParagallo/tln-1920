class Concept:
    def __init__(self, id=None, genus_bag=None, definitions=None):
        self.__id=id
        self.__genus_bag = genus_bag if genus_bag else []
        self.__definitions = definitions if definitions else []

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id

    def get_genus_bag(self):
        return self.__genus_bag

    def set_genus_bag(self, genus_bag):
        self.__genus_bag = genus_bag

    def get_genus_hypernyms_bag(self):
        return self.__genus_hypernyms_bag

    def set_genus_hypernyms_bag(self, genus_hypernyms_bag):
        self.__genus_hypernyms_bag = genus_hypernyms_bag

    def get_definitions(self):
        return self.__definitions

    def set_definitions(self,definitions):
        self.__definitions = definitions

    def get_corpus(self):
        return self.__corpus

    def set_corpus(self, corpus):
        self.__corpus = corpus

    def get_preprocessed_corpus(self):
        return self.__preprocessed_corpus

    def set_preprocessed_corpus(self, preprocessed_corpus):
        self.__preprocessed_corpus = preprocessed_corpus


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

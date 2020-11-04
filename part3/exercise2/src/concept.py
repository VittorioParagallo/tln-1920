class Concept:
    def __init__(self, id=None, genus_bag=[], definitions=[]):
        self.__id=id
        self.__genus_bag = genus_bag
        self.__definitions = definitions

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


class Genus:

    def get_lemma(self):
        return self.__lemma

    def set_lemma(self, lemma):
        self.__lemma = lemma

    def get_frequency(self):
        return self.__frequency

    def set_frequency(self, frequency):
        self.__frequency = frequency

    def get_synset(self):
        return self.__synset

    def set_synset(self, synset):
        self.__synset = synset

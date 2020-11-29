

class SintaticNode:

    def get_id(self):
        return self.__id

    def set_id(self, id):
        self.__id = id
          
    def get_pos(self):
        return self.__pos

    def set_pos(self, pos):
        self.__pos = pos

    def get_lemma_ita(self):
        return self.__lemma_ita

    def set_lemma_ita(self, lemma_ita):
        self.__lemma_ita = lemma_ita

    def get_lemma_eng(self):
        return self.__lemma_eng

    def set_lemma_eng(self, lemma_eng):
        self.__lemma_eng = lemma_eng

    def get_original_token(self):
        return self.__original_token

    def set_original_token(self, original_token):
        self.__original_token = original_token

    def get_head_id(self):
        return self.__head_id

    def set_head_id(self, head_id):
        self.__head_id = head_id

    def get_dependency(self):
        return self.__dependency

    def set_dependency(self, dependency):
        self.__dependency = dependency

    def get_sintax(self):
        return self.__sintax

    def set_sintax(self, sintax):
        self.__sintax = sintax

    
    def __str__(self):
        return  '\t'.join(('{} = {}'.format( item[15:], self.__dict__[str(item)]) for item in self.__dict__))

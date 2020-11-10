

class SynNode:
    def __init__(self, synset=None, is_explored=False, childen_nodes=None, weight=1, graph_level=0, similarity_value=None):
        self._synset = synset
        self._is_explored = is_explored
        self._childen_nodes = childen_nodes if childen_nodes else[]
        self._weight = weight
        self._graph_level = graph_level
        self._similarity_value = similarity_value


    def get_childen_nodes(self):
        return self._childen_nodes

    def set_childen_nodes(self, childen_nodes):
        self._childen_nodes = childen_nodes

    def get_is_explored(self):
        return self._is_explored

    def set_is_explored(self, is_explored):
        self._is_explored = is_explored

    def get_weight(self):
        return self._weight

    def set_weight(self, weight):
        self._weight = weight

    def get_graph_level(self):
        return self._graph_level

    def set_graph_level(self, graph_level):
        self._graph_level = graph_level

    def get_synset(self):
        return self._synset

    def set_synset(self, synset):
        self._synset = synset

    def get_similarity_value(self):
        return self._similarity_value

    def set_similarity_value(self, similarity_value):
        self._similarity_value = similarity_value

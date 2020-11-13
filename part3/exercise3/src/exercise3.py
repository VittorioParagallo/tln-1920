import nltk
from nltk.parse.corenlp import CoreNLPDependencyParser
from nltk.corpus import brown
from nltk.stem import WordNetLemmatizer
from nltk.wsd import lesk
from graphviz import Source
from utilities.OurDependencyGraph import OurDependencyGraph
from utilities.our_lesk import our_lesk
import spacy
from spacy import displacy
from corenlp_dtree_visualizer.converters import _corenlp_dep_tree_to_spacy_dep_tree
import itertools
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
# global parameter for WordNet search
verbs_pos = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
subj_dept = ['nsubj', 'nsubjpass']
obj_dept = ['dobj', 'iobj', 'obj']

personal_pronoun_tags = ['PRP']
tag_to_wnpos_map = {
    'CC': None,  # coordin. conjunction (and, but, or)
    'CD': [wn.NOUN],  # cardinal number (one, two)
    'DT': None,  # determiner (a, the)
    'EX': [wn.ADV],  # existential ‘there’ (there)
    'FW': None,  # foreign word (mea culpa)
    'IN': [wn.ADV],  # preposition/sub-conj (of, in, by)
    'JJ': [wn.ADJ, wn.ADJ_SAT],  # adjective (yellow)
    'JJR': [wn.ADJ, wn.ADJ_SAT],  # adj., comparative (bigger)
    'JJS': [wn.ADJ, wn.ADJ_SAT],  # adj., superlative (wildest)
    'LS': None,  # list item marker (1, 2, One)
    'MD': None,  # modal (can, should)
    'NN': [wn.NOUN],  # noun, sing. or mass (llama)
    'NNS': [wn.NOUN],  # noun, plural (llamas)
    'NNP': [wn.NOUN],  # proper noun, sing. (IBM)
    'NNPS': [wn.NOUN],  # proper noun, plural (Carolinas)
    'PDT': [wn.ADJ, wn.ADJ_SAT],  # predeterminer (all, both)
    'POS': None,  # possessive ending (’s )
    'PRP': None,  # personal pronoun (I, you, he)
    'PRP$': None,  # possessive pronoun (your, one’s)
    'RB': [wn.ADV],  # adverb (quickly, never)
    'RBR': [wn.ADV],  # adverb, comparative (faster)
    'RBS': [wn.ADV],  # adverb, superlative (fastest)
    'RP': [wn.ADJ, wn.ADJ_SAT],  # particle (up, off)
    'SYM': None,  # symbol (+,%, &)
    'TO': None,  # “to” (to)
    'UH': None,  # interjection (ah, oops)
    'AUX': [wn.VERB],
    'VB': [wn.VERB],  # verb base form (eat)
    'VBD': [wn.VERB],  # verb past tense (ate)
    'VBG': [wn.VERB],  # verb gerund (eating)
    'VBN': [wn.VERB],  # verb past participle (eaten)
    'VBP': [wn.VERB],  # verb non-3sg pres (eat)
    'VBZ': [wn.VERB],  # verb 3sg pres (eats)
    'WDT': None,  # wh-determiner (which, that)
    'WP': None,  # wh-pronoun (what, who)
    'WP$': None,  # possessive (wh- whose)
    'WRB': None,  # wh-adverb (how, where)
    '$': None,  # dollar sign ($)
    '#': None,  # pound sign (#)
    '“': None,  # left quote (‘ or “)
    '”': None,  # right quote (’ or ”)
    '(': None,  # left parenthesis ([, (, {, <)
    ')': None,  # right parenthesis (], ), }, >)
    ',': None,  # comma (,)
    '.': None,  # sentence-final punc (. ! ?)
    ':': None  # mid-sentence punc (: ; ... – -)
}
def hanks(verb):
    """
    Implementation of P. Hanks theory.
    Given a transitive verb, we find N sentences in the Brown corpus that
    contains the given verb. We do WSD (using 2 version of Lesk algorithm,
    one handwritten by us and the other from NLTK library) on the verb
    arguments (subj and obj), and finally, we compute the Filler's supersense
    incidence rate.
    """

    fillers = []  # [(subj, obj, sentence)]

    # Set the URI to communicate with Stanford CoreNLP
    # launch server first from StanfordCoreNLP folder:
    # java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
    dependency_parser = CoreNLPDependencyParser(url="http://localhost:9000")

    print('[1] - Extracting sentences...')
    """
    It analyzes the Brown Corpus and extracts the sentences containing the
    desired verb given as global input.
    :return: list of sentences (in which each sentence is a list of words)
    """
    # if you want to filter sentences by category
    # list_sent = brown.sents(categories=['news'])
    sentences = [' '.join(sent).strip().lower().replace('.', '')
                 for sent in brown.sents()
                 if verb in
                 [WordNetLemmatizer().lemmatize(word_tag[0], 'v')
                  for word_tag in nltk.pos_tag(sent)
                  if word_tag[1] in verbs_pos]]

    print("\t{} sentences in which the verb \'{}\' appears.".format(
        str(len(sentences)), verb))

    print('\n[2] - Extracting fillers...')
    for sentence in sentences:
        # PoS Tagging
        tokens = nltk.word_tokenize(sentence)
        # dictionary of all PoS Tag of the tokens
        tags = dict(nltk.pos_tag(tokens))

        # Syntactic parsing
        result = dependency_parser.raw_parse(sentence)
        dep = next(result)
        # visualizza tree
        #for triple in dep.triples(): print(triple[1], "(", triple[0][0], ", ", triple[2][0], ")")

        # una lista di dipendenze in cui:
        # si cerca tra i nodi quelli con token verbo
        # tra essi quello che corrisponde al verbo dati in input
        # e si restituisce la lista di dipendenti se la dipendenza è quella indicata nei parametri
        tree_nodes = dep.nodes
        verbs_dependents_keys = [list(itertools.chain.from_iterable(list
                                                              (verb_node['deps'].values()))) for verb_node in tree_nodes.values()
                                                              if verb_node['tag'] in verbs_pos
                                                              and verb_node['lemma'] == verb]
        # and not set(verb_node['deps'].keys()).isdisjoint(subj_dept+obj_dept)

        for verb_dependent_keys in verbs_dependents_keys:
            verb_dependent_nodes = [(tree_nodes[index]['lemma'], tree_nodes[index]['rel'], tree_nodes[index]['tag'])
                                    for index in verb_dependent_keys]

            verb_dependent_nodes_filtered = list(
                filter(lambda x: x[1] in subj_dept or x[1] in obj_dept, verb_dependent_nodes))
        # disegna tree
        #Source(dep.to_dot(), filename="test.gv", format="png").view()

            if len(verb_dependent_nodes_filtered) == 2:

                filler_1_supersense = compute_supersense(
                    verb_dependent_nodes_filtered[0], sentence)
                filler_2_supersense = compute_supersense(
                    verb_dependent_nodes_filtered[1], sentence)
                # è una tripla  (filler 1, filler 2, sentence)
                # ogni filler è a sua volta una tripla con senso disambiguato, lemma, relazione col verbo
                if filler_1_supersense != None and filler_2_supersense != None:
                  fillers.append(((filler_1_supersense, verb_dependent_nodes_filtered[0][0], verb_dependent_nodes_filtered[0][1]),
                                (filler_2_supersense,
                                  verb_dependent_nodes_filtered[1][0], verb_dependent_nodes_filtered[1][1]),
                                sentence))

    print("\n[3] - Total of {} Fillers".format(str(len(fillers))))
    filler_result_log = "\n".join([("{} | ({}, {})  | {} | ({}, {}) | {}".format(
        f[0][0], f[0][1], f[0][2], f[1][0], f[1][1], f[1][2], f[2])) for f in fillers])

    print(filler_result_log)
    
    text_file = open("./part3/exercise3/reports/" +
                     verb+ "_fillers.csv", "w")
    text_file.write(filler_result_log)
    text_file.close()




    nltk_lesk_semantic_types = {}  # {(s1, s2): count}
    for f in fillers:

      if (f[0][0],f[1][0]) in nltk_lesk_semantic_types.keys():
          nltk_lesk_semantic_types[(f[0][0], f[1][0])] += 1
      elif (f[1][0], f[0][0]) in nltk_lesk_semantic_types.keys():
          nltk_lesk_semantic_types[(f[1][0], f[0][0])] += 1
      else:
          nltk_lesk_semantic_types[(f[0][0], f[1][0])] = 1


    print('\n[4.2] - "NLTK Lesk":\n\tFinding Semantic Clusters (percentage, count of instances, semantic cluster):')
    tot = len(fillers)    
    clusters_results = "\n".join(["{} | {} | {}%".format(cluster[0], cluster[1], str(round((cluster[1] / tot)
                                                                                           * 100, 2))) for cluster in sorted(nltk_lesk_semantic_types.items(), key=lambda x: x[1], reverse=True)])
    print(clusters_results)
    text_file = open("./part3/exercise3/reports/" +
                         verb + "_clusters.csv", "w")
    text_file.write(clusters_results)
    text_file.close()

#receives a tuple like ('celery', 'obj', 'NN')
#returns a super sense
def compute_supersense(tuple, sentence):
  if tuple[2] in personal_pronoun_tags:
    return 'noun.person' if tuple[0] != 'it' else 'noun.entity'
  if tuple[0] == 'who':
    return 'noun.person'
  if tuple[0] == 'what':
    return 'noun.entity'
  # Ex. in sentence: interest in how what people eat affects their health
  # ('what', 'obj', 'WP') what sense returns no sense
  # force to entity
  if tag_to_wnpos_map[tuple[2]] is not None:
    #ottieni la lista di wn pos abbinata al tag penn e calcola il sinset con lesk per ognuno di questi 
    possible_syns_by_pos = [x for x in
                                          [lesk(sentence, tuple[0], pos=pos) for pos in tag_to_wnpos_map[tuple[2]]]
                                          if x is not None]
    #usa lesk per disambiguare tra i synset trovati
    filler_sense = lesk(sentence, tuple[0], synsets=possible_syns_by_pos)
  else:
    filler_sense = lesk(sentence, tuple[0])


  filler_supersense = filler_sense.lexname(
      ) if filler_sense is not None else None
  return filler_supersense


if __name__ == "__main__":
    """
    IMPORTANT: Before run, make sure to download Stanford CoreNLP 4.1.0 tool
    and run it using the following command inside its root folder. 

    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000

    After that, you can run this exercise.
    """

    # take, put, give, get, meet
    verb = input("Enter a verb to search in the Brown corpus: ")
    hanks(verb)

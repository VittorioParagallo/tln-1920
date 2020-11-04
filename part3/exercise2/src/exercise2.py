import csv
import nltk
import pprint
import string
import random
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from IPython.core.display import display, HTML
from sklearn.feature_extraction.text import CountVectorizer
from nltk.wsd import lesk
from pandas.core.common import flatten
import itertools
from collections import Counter
from definition import Definition
from concept import Concept, Genus


def load_data(data_file_url):
    """
    It reads che definition's CSV
    :return: four list containing the read definitions.
    """
    with open(data_file_url, "r",  encoding='utf-8-sig') as content:
        concept_definitions_dict = {}
        for i, concept_row in enumerate(csv.reader(content, delimiter=';')):
            # preprocess all the definitions
            concept = Concept(concept_row[0])
            concept.set_definitions([Definition(rawText=definition, preprocessed=preprocess(
                definition)) for definition in concept_row[1:]])

            # set the corpus as the merge of all raw definitions
            concept.set_corpus(". ".join(
                map(Definition.get_raw, concept.get_definitions())))
            # set the preprocessed corpus as the merge of all preprocessed  definitions
            concept.set_preprocessed_corpus(list(itertools.chain(
                *list((map(Definition.get_preprocessed, concept.get_definitions()))))))

            concept_definitions_dict[i] = concept
         # save the result in html table for logging purpose
        save_html_intermediate_data(pd.DataFrame(
            [x.get_definitions() for x in concept_definitions_dict.values()]), 'load_data_log.html', "Preprocessed loaded data")

        return concept_definitions_dict

# function to save log in html tables


def save_html_intermediate_data(dataframe, filename, caption="", crosscell="", summary=""):
  columns =  dataframe.columns.to_list()
  columns = list(zip([summary] * len(columns), columns))
  columns = pd.MultiIndex.from_tuples(columns, names=['-', crosscell])
  dataframe.columns = columns
  styles = [{'props': [("font-family", "Calibri")]}, {
        'selector': 'th',
        'props': [
            ('background-color', 'rgba(0, 0, 128, 0.3)'),
           # ('opacity', '0.3'),
            ('color', 'black'),
            ('text-align', 'left'),
        ]  # for alignment
    },
        {
        'selector': 'td',
        'props': [
            ('border-collapse', 'collapse'),
            ('border', '1px solid silver'),
        ]
    },]

  s = dataframe.style.set_table_styles(styles).highlight_max(
        color='lightgreen').highlight_min(color='#cd4f39').set_caption(caption)
  html_text = s.render().replace('\\t', '<br/> <br/>').replace('nan', '').replace("Synset","")
    # dataframe.to_html(filename)
  with open("./part3/exercise2/reports/html/"+filename, 'w') as f:
    f.write(html_text)


stop_words = set(stopwords.words('english'))
wnl = nltk.WordNetLemmatizer()


def preprocess(text):
    """
    It does some preprocess: removes stopwords, punctuation and does the
    lemmatization of the tokens inside the sentence.

    :param definition: a string representing to preprocess
    :return: a lost of strings which contains the preprocessed string tokens, lemmantized and wiyhout stopwords.
    """

    # tokenize dentence
    text_tokenized = word_tokenize(text)
    # add pos tag and convert each touple  ("church","NN") to list  ["church","NN"] because touples are unmodifiable
    text_tokenized_postag = [list(tok) for tok in nltk.pos_tag(text_tokenized)]
    # remove punctuation and stopwords
    text_tok_postag_nopunct_nostop = list(filter(lambda x: (x[0] not in string.punctuation) and (
        x[0] not in stop_words), text_tokenized_postag))
   # replace word with lemma
    for token in text_tok_postag_nopunct_nostop:
        token[0] = wnl.lemmatize(token[0])
    return text_tok_postag_nopunct_nostop


def findConcept(concept):
    print('working on concept: '+str(concept.get_id()))
    # merge all the definitions as 1 corpus
    all_definitions_possible_genuses = []
    all_definitions_possible_genuses_hypernyms = []
    # processa le definizioni per individuare candidati genus
    for definition in concept.get_definitions():
        print('analizing definition:'+definition.get_raw())
        # estrai solo i lemmi taggati 'NN' (inserire anche JJ???)
        possible_genuses = [x[0] for x in list(filter(lambda x: x[1] in ["NN"] , definition.get_preprocessed()))]
        # disambigua rispetto a tutte le definizioni dello stesso concetto come se fosse un unico corpus.
        # eventualmente provare la differenza disambiguando solo con la definizione in cui è contenuto
        possible_genuses_syns = list(filter(None, [lesk(concept.get_corpus(), possible_genus)
                                 for possible_genus in possible_genuses]))
        # aggiungi alla lista di genus di tutte le definizioni del concetto
        # Es. [Synset('recognition.n.08'), Synset('respect.n.01')]
        all_definitions_possible_genuses.extend(possible_genuses_syns)
        # save the list of all the genuses hypernyms
        all_definitions_possible_genuses_hypernyms.extend(
            list(itertools.chain(*[genus_syn.hypernyms() for genus_syn in possible_genuses_syns if len(possible_genuses_syns)>0 and len(genus_syn.hypernyms()) > 0])))
    # associa al concetto il genus bag pesato.
    # è un dizionario con synset del genus in chiave e #occorrenze in valore
    # Es Counter({Synset('recognition.n.08'): 1, Synset('respect.n.01'): 1})
    concept.set_genus_bag(Counter(all_definitions_possible_genuses))
    concept.set_genus_hypernyms_bag(
        Counter(all_definitions_possible_genuses_hypernyms))
    
    
    # FIRST EXPERIMENT:
    # given the genus and its hyponyms compute these hyponyms similarities vs. definition corpus
    #
    #

    # compute the total freqencies in the genus bag
    # example:
    # on {Synset('concept.n.01'): 3, Synset('paleness.n.02'): 2, Synset('outline.n.02'): 2}
    # tot_frequencies= 7

    genus_hypo_similarities = noun_hypo_analisys(concept)
    # associa ad ogni genus l'iponimo con max similarità
    local_genus_hypo_max_dict = {
        key: max(val.values()) for key, val in genus_hypo_similarities.items()}
    # l'iponimo con similarita massima globale    
    global_genus_hypo_max = max(
        local_genus_hypo_max_dict, key=local_genus_hypo_max_dict.get, default=None)
    # log results
    save_html_intermediate_data(pd.DataFrame(genus_hypo_similarities),\
                                'concept ' + str(concept.get_id()) + ' genus_hypons_similarities.html', \
                                'Genus -> hypo: similarity\n Concept:' + str(concept.get_id()), \
                                  'HYPONYMS \ GENUSES', \
                                'local max: <br>' + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join([str(v).replace("Synset('", '').replace("')", '')+' : '+str(k)[:8] for v, k in local_genus_hypo_max_dict.items()])+'<br/>overall max:'+str(global_genus_hypo_max))

    # SEECOND EXPERIMENT:
    # given the genus and its hyponyms compute these hyponyms similarities vs. definition corpus
    #
    #
    genus_hype_hypo_similarities = noun_hype_hypo_analisys(concept)
    # associa ad ogni genus l'iponimo con max similarità
    local_hype_hypo_max_dict = {
        key: max(val.values()) for key, val in genus_hype_hypo_similarities.items()}
    # l'iponimo con similarita massima globale
    global_hype_hypo_max = max(
        local_hype_hypo_max_dict, key=local_hype_hypo_max_dict.get, default=None)
    # log results
    save_html_intermediate_data(pd.DataFrame(genus_hype_hypo_similarities),
                                'concept ' + str(concept.get_id()) + ' genus_hype_hypons_similarities.html', \
                                'Genus-> hype -> hypo: similarity\n Concept:' + str(concept.get_id()), \
                                      'HYPONYMS \ HYPERONYMS (of genuses)',
                                'local max: <br>' + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join([str(v).replace("Synset('", '').replace("')", '') + ' : ' + str(
                                    k)[:8] for v, k in local_hype_hypo_max_dict.items()]) + '<br/>overall max:' + str(global_hype_hypo_max)
                                  )

    return "\t{}: \t{}\t\t{}".format(str(concept.get_id()),
                                     global_genus_hypo_max.name() if global_genus_hypo_max is not None else 'N/A', global_hype_hypo_max.name() if global_hype_hypo_max is not None else 'N/A')


def noun_hypo_analisys(concept):
  tot_frequencies = sum(concept.get_genus_bag().values())
  genus_hypons_similarities = {}
  for genus in concept.get_genus_bag():
      #genus = max(concept.get_genus_bag(), key=concept.get_genus_bag().get)

      # compute the genus normalized weight based on its frequency over all frequencies
      genus_weight = (1 / tot_frequencies) * concept.get_genus_bag()[genus]

      # return all the genus hypons with similarity values !=0
      # all similarity values are weighted with genus weight
      # Example{Synset('hypothesis.n.02'): 0.005906564752148317, Synset('quantity.n.03'): 0.0075294222323759}
      hypons_analisys = compute_hypons_similarity(
           concept, genus, genus_weight
           )
       # add to the genus_hypons_similarities only if the genus has hypons or these have similariity values
       # Ex. paleness doesn't have hyponyms
      if(len(hypons_analisys) > 0):
            genus_hypons_similarities[genus] = compute_hypons_similarity(
                concept, genus, genus_weight
                )
      else:
            print(genus.name() + "has no hyponyms or similarities with corpus")
  return genus_hypons_similarities


def noun_hype_hypo_analisys(concept):
  tot_frequencies = sum(concept.get_genus_hypernyms_bag().values())
  hype_hypons_similarities = {}
  for hype in concept.get_genus_hypernyms_bag():
      #genus = max(concept.get_genus_bag(), key=concept.get_genus_bag().get)

      # compute the genus normalized weight based on its frequency over all frequencies
      hype_weight = (1 / tot_frequencies) * concept.get_genus_hypernyms_bag()[hype]

      # return all the genus hyperyms with similarity values !=0
      # all similarity values are weighted with genus weight
      # Example{Synset('hypothesis.n.02'): 0.005906564752148317, Synset('quantity.n.03'): 0.0075294222323759}
      hypons_analisys = compute_hypons_similarity(
          concept, hype, hype_weight
          )
      # add to the genus_hypons_similarities only if the genus has hypons or these have similariity values
      # Ex. paleness doesn't have hyponyms
      if(len(hypons_analisys) > 0):
          hype_hypons_similarities[hype] = compute_hypons_similarity(
              concept, hype, hype_weight)
      else:
          print(hype.name() + "has no hyponyms or similarities with corpus")
  return hype_hypons_similarities

def compute_hypons_similarity(concept, genus_syn, genus_weight):
    all_hypon = list(genus_syn.closure(
        lambda s: genus_syn.hyponyms(), depth=1))
    # creates a dictionary like
    #{Synset('hypothesis.n.02'): 0.005906564752148317, Synset('quantity.n.03'): 0.0075294222323759}
 # k=hypon, v=weighted cosine similarity  between definitions corpus and hypon definition
 # the weight is normalized frequency of genus in corpus
 #hypon_corpus is the merge of the hyponyn definition and examples
    hypon_analisys_dict = {(hypon, \
                                         cos_similarity( \
                                            preprocess(\
                                                  hypon.definition()  \
                                             #+ ". ".join(hypon.examples())+ \
                                             #" ".join([lemma.name() for lemma in hypon.lemmas()])
                                             #" ".join([lemma.name() for lemma in list(itertools.chain(*[sub_hypon.lemmas() for sub_hypon in hypon.hyponyms()]))])\
                                            ),
                                             concept.get_preprocessed_corpus()\
                                           # " ".join([lemma.name() for lemma in list(itertools.chain(*[genus_syn.lemmas() for genus_syn in concept.get_genus_bag()]))])
                                              ) \
                                          *genus_weight)
                           for hypon in all_hypon}
    # return the result omitting the ones with 0 similarity
    return {k: v for k, v in hypon_analisys_dict if v != 0}


def cos_similarity(sentence_1, sentence_2):
    if (len(sentence_1) == 0 or len(sentence_2) == 0):
      return 0.0
    if (len(sentence_1) == 0 and len(sentence_2) == 0):
      return 1.0
    X_set = {w[0] for w in sentence_1}
    Y_set = {w[0] for w in sentence_2}
    l1 = []
    l2 = []
    # form a set containing keywords of both strings
    rvector = X_set.union(Y_set)

    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    # cosine formula
    for i in range(len(rvector)):
        c += l1[i]*l2[i]
    return c / float((sum(l1)*sum(l2))**0.5)


def genus_hyper(concept_definitions_dict):
    content = concept_definitions_dict  # Loading the content-to-form.csv file

    for index in content:
        genus_dict = {}
        hyponyms_list = []

        for definition in content[index].get_definitions():
            hypernyms = []
            hyponyms = []
            clean_tokens = definition.get_preprocessed()

            for word in clean_tokens:
                syn = [lesk(definition.get_raw(), word)]
                if len(syn) > 0:  # needed because for some words lesks returns an empty list
                    for s in syn:
                        if s:
                            def hyper(s): return s.hypernyms()
                            all_hyper = list(s.closure(hyper, depth=1))
                            hypernyms.extend([x.name().split(".")[0]
                                              for x in all_hyper])

                    for g in hypernyms:
                        if g not in genus_dict:
                            genus_dict[g] = 1
                        else:
                            genus_dict[g] += 1

            if len(genus_dict) > 0:
                genus = max(genus_dict, key=genus_dict.get)
                syns = wn.synsets(genus)

                # W e take every hyponyms for the Genus of the definition
                for i, s in enumerate(syns, start=0):
                    def hypon(s): return s.hyponyms()
                    all_hypon = list(s.closure(hypon, depth=1))
                    hyponyms.extend([x.name().split(".")[0]
                                     for x in all_hypon])

            hyponyms_list.append(' '.join(hyponyms))

        # CountVectorizer will create k vectors in n-dimensional space, where:
        # - k is the number of sentences,
        # - n is the number of unique words in all sentences combined.
        # If a sentence contains a certain word, the value will be 1 and 0 otherwise
        vectorizer = CountVectorizer()
        matrix = vectorizer.fit_transform(hyponyms_list)

        feature_list = vectorizer.get_feature_names()
        vectors = matrix.toarray()

        # Index of the element with maximum frequency across all the definition of a concept
        m = vectors.sum(axis=0).argmax()

        print("\t{} - {} - {}".format(index + 1, feature_list[m], m))


if __name__ == "__main__":

    concept_definitions_dict = load_data(
        "./part3/exercise2/input/content-to-form.csv")

    print("\tid\t(genus->hypo)\t\t(genus->hype->hypo)\n"+"\n".join([findConcept(concept)
           for concept in concept_definitions_dict.values()]))
  
   # print("\nGenus Hyper")
   #genus_hyper(concept_definitions_dict)

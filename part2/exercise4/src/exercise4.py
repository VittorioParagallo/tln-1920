import re
import sys
from pathlib import Path
import numpy as np
from numpy import mean
import requests
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics.pairwise import cosine_similarity
import csv
import itertools
import numpy as np
def get_synset_terms(sense):
    """
    It use the BabelNet HTTP API for getting the first three Lemmas of the word
    associated to the given Babel Synset ID.
    :param sense: sense's BabelID
    :return: the first three lemmas of the given sense. An error string if
    there are none
    """

    req = requests.get("https://babelnet.io/v5/getSynset",
                       {"id": sense,
                        "key": "67adc825-bbcc-4cd4-8d6c-71ecdb875e7c",  # API key
                        "targetLang": "IT"})  # only italian results
    data = req.json()
    synset_terms = set()

    for sense in data["senses"]:
        term = sense["properties"]["fullLemma"]
        synset_terms.add(term.replace('\_', ' ').lower())
        if len(synset_terms) == 3:
            break

    return list(synset_terms) if synset_terms else "No synset terms"

def parse_nasari():
    """
    It parses the NASARI's Embedded input.
    :return: First: a dictionary in which each BabelID is associated with the
    corresponding NASARI's vector. Second: a lexical dictionary that associate
    to each BabelID the corresponding english term.

    {babelId: [nasari vector's values]}, {babelID: word_en}
    """
    babel_word_nasari = {}
    nasari = {}
    # prendo tutte le righe del file
    lines = tuple(open(config["nasari"], 'r'))
    for line in lines:
        bn, term, *values = re.split('__|\t', line)
        babel_word_nasari[bn] = term
        nasari[bn] = list(map(float, values))

    return nasari, babel_word_nasari

def parse_italian_synset():
    """
    It parses SemEvalIT17 file. Each italian term is associated with a list of
    BabelID.
    :return: a dictionary containing the italian word followed by the list of
    its BabelID. Format: {word_it: [BabelID1,BabelID2.. BabelIDN]}
    """
    filetext = Path(config["input_italian_synset"]).read_text()
    itWords_bnsns_dict = {}
    # get all the portion of file between # regex:(?<=#)(?s:.)*?(?=#)
    term_bnsns_text_groups = filetext.split('#')[1:]
    for term_bnsns_text_group in term_bnsns_text_groups:
        # get all the text elements between \n regex:(?<=\n)(?s:.)*?(?=\n) re.MULTILINE    re.findall(r'.*?(?=\n)
        term, *bnsns = re.findall(r'(.*?)[\n]', term_bnsns_text_group)
        itWords_bnsns_dict[term.lower()] = bnsns
    return itWords_bnsns_dict

def parse_input_words(path):
    """
    it parses the annotated words's file.
    :param path to the annotated word's file.
    :return: list of annotated terms. Format: [((w1, w2), value)]
    """
    reader = csv.reader(open(path, 'r', encoding="utf-8-sig"), delimiter='\t')
    return [(row[0].lower(), row[1].lower(), float(row[2]))
            for row in reader]

def parse_sense(path):
    """
    it parses the senses in the file.
    :param path to the senses file.
    :return: list of annotated senses and associated terms. Format: [(s1, s2, t1, t2)]
    """
    reader = csv.reader(open(path, 'r', encoding="utf-8-sig"), delimiter='\t')
    return list(tuple(
        map(lambda x: x.lower(), line))
        for line in reader)

def best_sense_couple_by_words(bnsn_ids_word1, bnsn_ids_word2, nasari_dict):
    """
    It computes the couple with max cosine similarity among its Embedded NASARI vectors
    :param bnsn_ids_word1: list of BabelID of the first word
    :param bnsn_ids_word2: list of BabelID of the second word
    :param nasari_dict: NASARI dictionary
    :return: the couple of senses (their BabelID) that maximise the score and
    the cosine similarity score.
    """
    # creates all the combinations of bn_syns1 and bn_syns2 which are present in nasari_dict.keys()
    # for each combination computes the cosine sym and store the list as a triple syn1, syn2, score
    similarities = [(x,
                     y,
                     cosine_similarity([nasari_dict[x]], [nasari_dict[y]])[0][0])
                    for x in bnsn_ids_word1
                    for y in bnsn_ids_word2
                    if set([x, y]).issubset(nasari_dict.keys())]
    # find the the couple with max score or returns  (None,None,0)
    max_value = max(similarities, key=lambda x: x[2], default=(None, None, 0))
    return (max_value[0], max_value[1]), max_value[2]

def evaluate_correlation_level(v1, v2):
    """
    It evaluates the correlation between the system annotations (v2) and the
    human annotations (v1) using Pearson and Spearman  metrics.
    :param v1: the first annotated vector (human annotations)
    :param v2: the second annotated vector (algorithm annotations)
    :return: Pearson and Spearman indexes
    """
    return pearsonr(v1, v2)[0], spearmanr(v1, v2)[0]

# Dictionary containing all the script settings. Used everywhere.
global config

if __name__ == "__main__":

  config = {
      "input_senses": "./part2/exercise4/input/mydata/my_senses.tsv",
      "input_italian_synset": "./part2/exercise4/input/SemEval17_IT_senses2synsets.txt",
      "nasari": "./part2/exercise4/input/mini_NASARI.tsv",
      "output": "./part2/exercise2/output/"
  }

  nasari_dict, babel_word_nasari = parse_nasari()
  italian_senses_dict = parse_italian_synset()

  print('Task 1: Semantic Similarity')

  input_words_goldscore = parse_input_words(
      './part2/exercise4/input/1st_assignment_50_couples_manually_annotated.tsv')

  # 1. Annotation's scores, used for evaluation
  golden_scores =[]
  computed_scores=[]
  # 3. Computing the cosine similarity between the hand-annotated scores and
  # Nasari best score given the two terms
  computed_annotation_results = []

  for word_1, word_2, goldscore in input_words_goldscore:  # is equal to use input_words_goldscore or annotations_2, because the words are the same

    (s1, s2), score = best_sense_couple_by_words(
                                      italian_senses_dict[word_1],
                                      italian_senses_dict[word_2],
                                      nasari_dict)
    # normalize the score on 4 to be coherent with golden annotation    
    computed_annotation_results.append([word_1, word_2, score * 4])
    golden_scores.append(goldscore)
    computed_scores.append(score)

  pearson, spearman = evaluate_correlation_level(golden_scores, computed_scores)

  csv.writer(open('./part2/exercise4/output/1st_assignment_50_couples_computer_annotated.tsv',
                  "w"), delimiter='\t').writerows(computed_annotation_results)
  print(
      '\tEvaluation - Person: {0:.2f}, Spearman: {1:.2f}'.format(pearson, spearman))

  # ------------------------------------------------------------------------------------------------------------------

  print("\nTask 2: Sense Identification.")
  # Task 2: Sense Identification
  #
  # 1. annotate by hand the couple of words in the format specified in the README
  # 3. Compute the cosine similarity between the hand-annotated scores and
  # Nasari best score given the two terms
  # 4. Evaluate the total quality using the argmax function. Evaluate both
  # the single sense and both the senses in the couple.

#    senses = parse_sense('./part2/exercise4/input/mydata/my_senses.tsv')
  input_words_goldscore = parse_input_words(
      './part2/exercise4/input/1st_assignment_50_couples_manually_annotated.tsv')

    
  with open(config["output"] + 'results.tsv', "w", encoding="utf-8") as out:
    # used for final comparison. It is a in-memory copy of the output file
    result = []
    evaluations=[]
    for word_1, word_2, _ in input_words_goldscore:
        (s1, s2), _ = best_sense_couple_by_words(
            italian_senses_dict[word_1], italian_senses_dict[word_2], nasari_dict)

        # if both Babel Synset exists and are not None
        if s1 is not None and s2 is not None:
            out_terms_1 = get_synset_terms(s1)
            out_terms_2 = get_synset_terms(s2)
            result.append(
            (word_1, word_2, s1, s2, ','.join(out_terms_1), ','.join(out_terms_2)))

            #evaluation params
            s1s2_nasarivectors = [nasari_dict[s1], nasari_dict[s2]]
            word1_nasarivectors = [nasari_dict[bnsnId]
                                   for bnsnId in italian_senses_dict[word_1] if bnsnId in nasari_dict]
            word2_nasarivectors = [nasari_dict[bnsnId]
                                   for bnsnId in italian_senses_dict[word_2] if bnsnId in nasari_dict]
            sim_s1s2_vs_word1 = np.mean(cosine_similarity(
                                                              s1s2_nasarivectors,
                                                              word1_nasarivectors))
            sim_s1s2_vs_word2 = np.mean(cosine_similarity(
                                                                    s1s2_nasarivectors,
                                                                    word2_nasarivectors))
            sim_s1s2_vs_word1word2 = np.mean(cosine_similarity(
                                                                        s1s2_nasarivectors,
                                                                        word1_nasarivectors + word2_nasarivectors))
            avg_sim_score = (  sim_s1s2_vs_word1 +
                             sim_s1s2_vs_word2 +sim_s1s2_vs_word1word2)/3
            evaluations.append(
                (sim_s1s2_vs_word1, sim_s1s2_vs_word2, sim_s1s2_vs_word1word2,  avg_sim_score))
    
    csv.writer(open('./part2/exercise4/output/2nd_assignment_bnsyns_retrieval.tsv',
                    "w"), delimiter='\t').writerows(result)

    print("\n\tAccuracy: ({:.0f}%)".format(
        np.mean([similarity[2] for similarity in evaluations])*100))

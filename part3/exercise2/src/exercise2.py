import csv
import nltk
import pprint
import imgkit
import fitz
import img2pdf
import string
import random
import os
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
from experiments_list import experiments_parameters


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

            concept.set_id(
                lesk(concept.get_corpus().split(), (concept.get_id())))

            concept_definitions_dict[i] = concept

         # save the result in html table for logging purpose
        save_html_intermediate_data(pd.DataFrame(
            [x.get_definitions() for x in concept_definitions_dict.values()]), 'load_data_log.html', "Preprocessed loaded data")

        return concept_definitions_dict

# function to save log in html tables


def save_html_intermediate_data(dataframe, filename, caption="", crosscell="", summary="", scorecell="-"):
    columns = dataframe.columns.to_list()
    columns = list(zip([summary] * len(columns), columns))
    columns = pd.MultiIndex.from_tuples(columns, names=[scorecell, crosscell])
    dataframe.columns = columns
    styles = [{'props': [("font-family", "Calibri")]}, {
        'selector': 'th',
        'props': [
              ('background-color', 'LightGrey'),
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
    }, ]

    s = dataframe.style.set_table_styles(styles).highlight_max(
        color='lightgreen').highlight_min(color='#cd4f39').set_caption(caption)
    html_text = s.render().replace(
        '\\t', '<br/> <br/>').replace('nan', '').replace("Synset", "")
    # dataframe.to_html(filename)
    html_filepath = "./part3/exercise2/reports/html/" + \
        execution_parms["test_id"]+"/"
    if not os.path.exists(html_filepath):
      os.makedirs(html_filepath)
    png_filepath = html_filepath.replace("html", "png")
    if not os.path.exists(png_filepath):
      os.makedirs(png_filepath)
    pdf_filepath = html_filepath.replace("html", "pdf")
    if not os.path.exists(pdf_filepath):
      os.makedirs(pdf_filepath)
    html_filepath += filename
    png_filepath += filename
    pdf_filepath += filename

    # save as html
    with open(html_filepath, 'w') as f:
        f.write(html_text)
    # save as png
    # imgkit.from_file(html_filepath, png_filepath)
    # #save as pdf
    # doc = fitz.open()                            # PDF with the pictures
    # img = fitz.open(png_filepath)  # open pic as document
    # rect = img[0].rect                       # pic dimension
    # pdfbytes = img.convertToPDF()            # make a PDF stream
    # img.close()                              # no longer needed
    # imgPDF = fitz.open("pdf", pdfbytes)      # open stream as PDF
    # page = doc.newPage(width=rect.width,   # new page with ...
    #                     height=rect.height)  # pic dimension
    # page.showPDFpage(rect, imgPDF, 0)
    # # image fills the page
    # doc.save(pdf_filepath)


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

        possible_genuses = [x[0] for x in list(
            filter(lambda x: x[1] in execution_parms["genus_tags"], definition.get_preprocessed()))]
        # disambigua rispetto a tutte le definizioni dello stesso concetto come se fosse un unico corpus.
        # eventualmente provare la differenza disambiguando solo con la definizione in cui è contenuto
        if execution_parms["lesk_on_genus"]:
          possible_genuses_syns = list(filter(None, [
              lesk(concept.get_corpus().split(), possible_genus, 'n')
                if execution_parms['lesk_only_n']
                else lesk(concept.get_corpus().split(), possible_genus)
            for possible_genus in possible_genuses]))
        else:
          possible_genuses_syns = list(filter(None, list(itertools.chain(
              *[wn.synsets(possible_genus) for possible_genus in possible_genuses]))))
        # aggiungi alla lista di genus di tutte le definizioni del concetto
        # Es. [Synset('recognition.n.08'), Synset('respect.n.01')]
        all_definitions_possible_genuses.extend(possible_genuses_syns)
        # save the list of all the genuses hypernyms
        all_definitions_possible_genuses_hypernyms.extend(
            list(itertools.chain(*[genus_syn.hypernyms() for genus_syn in possible_genuses_syns if len(possible_genuses_syns) > 0 and len(genus_syn.hypernyms()) > 0])))
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
    # è un dict { (genus_syn:hypo_syn): similarity_value}
    local_genus_hypo_max_dict = {}
    # create a new dictionary to display genus frequencies in report on the column heads
    data_display = {}
    all_hypoId_found = set(pair[0] for pair in list(
        itertools.chain(*genus_hypo_similarities.values())))

    for key, value in genus_hypo_similarities.items():
        # local_maxes is a list of tuples (Synset, similarity) with the
        # maximum value, is a list because more synset with the
        # same similarity value are taken into account
        local_maxes = list(filter(lambda x: x[1] == max(
            value, key=lambda t: t[1])[1], value))

        for local_max in local_maxes:
            local_genus_hypo_max_dict[(key, local_max[0])] = local_max[1]

        genus_hiposId = set(pair[0] for pair in value)
        missing_hypo = all_hypoId_found - genus_hiposId
        genus_hypo_similarities[key].extend([(x, None) for x in missing_hypo])
        column_label = key.name() + "<br/> (f:" + \
                                str(dict(concept.get_genus_bag())[key]) + ")"
        data_display[column_label] = dict(value)

    global_genus_hypo_max = dict(filter(lambda x: x[1] == max(
            local_genus_hypo_max_dict.values()), local_genus_hypo_max_dict.items()))

    # log results

    # summary_row = 'local max: <br>' + '&nbsp;&nbsp;&nbsp;&nbsp;<font color="DarkBlue">'.join([str(k[0])+'</font>-><font color="DarkGreen">'+str(k[1])+'</font>:'+str(
    #    v)[:8] for k, v in local_genus_hypo_max_dict.items()])
    summary_row_template = '&nbsp;&nbsp;&nbsp;&nbsp;<font color="DarkBlue">{}</font><font color="DarkGreen"> -> </font><font color="Indigo">{}</font >: {}'
    summary_row = 'local max: <br>' + ''.join([summary_row_template.format(str(k[0]), str(k[1]), str(
        v)[:8]) for k, v in local_genus_hypo_max_dict.items()])

    summary_row += '<br/><br/>overall max: ' + \
        " ".join([str(k[0]) + ' -> ' + str(k[1]) + ': ' + str(v)
                  for k, v in global_genus_hypo_max.items()])

    summary_row = summary_row.replace("('", "").replace("')", '')
    save_html_intermediate_data(pd.DataFrame(data_display),
                                str(concept.get_id().name().split()[0]) +
                                ' genus_hypons_similarities.html',
                                "<b>"+execution_parms["test_id"]+'</b> Genus -> hypo: similarity\n Concept: ' +
                                str(concept.get_id()),
                                'HYPONYMS \ GENUSES',
                                summary_row,
                                '<font size="2">' + "<br/>".join(["{} = {}".format(k, v)
                                                                  for k, v in execution_parms.items() if k is not "test_id"]) + "</font><br/>" +
                                "<br/>".join(["SCORE: "+str(k[1].path_similarity(concept.get_id()))[:8]
                                              for k, v in global_genus_hypo_max.items()]))

    # SEECOND EXPERIMENT:
    # given the genus and its hyponyms compute these hyponyms similarities vs. definition corpus
    #
    #
    genus_hype_hypo_similarities = noun_hype_hypo_analisys(concept)



    local_genus_hype_hypo_max_dict = {}
    data_display = {}
    all_hypoId_found = set(pair[0] for pair in list(
        itertools.chain(*genus_hype_hypo_similarities.values())))

    for key, value in genus_hype_hypo_similarities.items():
        # local_maxes is a list of tuples (Synset, similarity) with the
        # maximum value, is a list because more synset with the
        # same similarity value are taken into account
        local_maxes = list(filter(lambda x: x[1] == max(
            value, key=lambda t: t[1])[1], value))

        for local_max in local_maxes:
            local_genus_hype_hypo_max_dict[(key, local_max[0])] = local_max[1]

        genus_hiposId = set(pair[0] for pair in value)
        missing_hypo = all_hypoId_found - genus_hiposId
        genus_hype_hypo_similarities[key].extend(
            [(x, None) for x in missing_hypo])
        column_label = key.name() + "<br/> (f:" + \
            str(dict(concept.get_genus_hypernyms_bag())[key]) + ")"
        data_display[column_label] = dict(value)

    global_genus_hype_hypo_max = dict(filter(lambda x: x[1] == max(
            local_genus_hype_hypo_max_dict.values()), local_genus_hype_hypo_max_dict.items()))

    # log results

    summary_row_template = '&nbsp;&nbsp;&nbsp;&nbsp;<font color="DarkBlue">{}</font><font color="DarkGreen"> -> </font><font color="Indigo">{}</font >: {}'
    summary_row = 'local max: <br>' + ''.join([summary_row_template.format(str(k[0]), str(k[1]), str(
        v)[:8]) for k, v in local_genus_hype_hypo_max_dict.items()])

    summary_row += '<br/><br/>overall max: ' + \
        " ".join([str(k[0]) + ' -> ' + str(k[1]) + ': ' + str(v)
                  for k, v in global_genus_hype_hypo_max.items()])

    summary_row = summary_row.replace("('", "").replace("')", '')

    save_html_intermediate_data(pd.DataFrame(data_display),
                                str(concept.get_id().name().split()[0]) +
                                ' genus_hype_hypons_similarities.html',
                                "<b>"+execution_parms["test_id"]+'</b> Genus-> hype -> hypo: similarity\n Concept:' +
                                str(concept.get_id()),
                                'HYPONYMS \ HYPERONYMS (of genuses)',
                                summary_row,
                                '<font size="2">' + "<br/>".join(["{} = {}".format(k, v)
                                                                  for k, v in execution_parms.items() if k is not "test_id"]) + "</font><br/>" +
                                "<br/>".join(["SCORE: "+str(k[1].path_similarity(concept.get_id()))[:8]
                                              for k, v in global_genus_hype_hypo_max.items()])
                                  )
    row_template = "{}|{}|{}"
    return "{}|{}|{}".format(str(concept.get_id()),
        row_template.format(
                      ", ".join([k[0].name()
                                for k, v in global_genus_hypo_max.items()]),
                      ", ".join([k[1].name()
                                for k, v in global_genus_hypo_max.items()]),
                          [str(compute_score(k[1], concept.get_id())).replace(".", ",") if k is not None else 'N/A' for k, v in global_genus_hypo_max.items()][0]),
        row_template.format(
        ", ".join([k[0].name()
                  for k, v in global_genus_hype_hypo_max.items()]),
        ", ".join([k[1].name()
                  for k, v in global_genus_hype_hypo_max.items()]),
        [str(compute_score(k[1], concept.get_id())).replace(".", ",") if k is not None else 'N/A' for k, v in global_genus_hype_hypo_max.items()][0]),).replace("Synset('", "").replace("')", "")


def compute_score(syn_x, syn_y):
   if execution_parms["score_type"] == "path_similarity":
     return syn_x.path_similarity(syn_y)
   if execution_parms["score_type"] == "lch_similarity":
     return syn_x.lch_similarity(syn_y)
   if execution_parms["score_type"] == "wup_similarity":
     return syn_x.wup_similarity(syn_y)



def noun_hypo_analisys(concept):
    tot_frequencies = sum(concept.get_genus_bag().values())
    genus_hypons_similarities = {}
    for genus in concept.get_genus_bag():
        # genus = max(concept.get_genus_bag(), key=concept.get_genus_bag().get)

        # compute the genus normalized weight based on its frequency over all frequencies
        genus_weight = (1 / tot_frequencies) * concept.get_genus_bag()[genus]

        # return all the genus hypons with similarity values !=0
        # all similarity values are weighted with genus weight
        # Example{Synset('hypothesis.n.02'): 0.005906564752148317, Synset('quantity.n.03'): 0.0075294222323759}
        hypons_analisys = compute_hypons_similarity(
            concept, genus, genus_weight, execution_parms["genus_hypo_depth"]
        )
        # add to the genus_hypons_similarities only if the genus has hypons or these have similariity values
        # Ex. paleness doesn't have hyponyms
        if(len(hypons_analisys) > 0):
            genus_hypons_similarities[genus] = hypons_analisys
    return genus_hypons_similarities


def noun_hype_hypo_analisys(concept):
    tot_frequencies = sum(concept.get_genus_hypernyms_bag().values())
    hype_hypons_similarities = {}
    for hype in concept.get_genus_hypernyms_bag():
        # genus = max(concept.get_genus_bag(), key=concept.get_genus_bag().get)

        # compute the genus normalized weight based on its frequency over all frequencies
        hype_weight = (1 / tot_frequencies) * \
            concept.get_genus_hypernyms_bag()[hype]

        # return all the genus hyperyms with similarity values !=0
        # all similarity values are weighted with genus weight
        # Example{Synset('hypothesis.n.02'): 0.005906564752148317, Synset('quantity.n.03'): 0.0075294222323759}
        hypons_analisys = compute_hypons_similarity(
            concept, hype, hype_weight, execution_parms["genus_hyper_hypo_depth"]
        )
        # add to the genus_hypons_similarities only if the genus has hypons or these have similariity values
        # Ex. paleness doesn't have hyponyms
        if(len(hypons_analisys) > 0):
            hype_hypons_similarities[hype] = hypons_analisys
    return hype_hypons_similarities


def compute_hypons_similarity(concept, root_syn, genus_weight, depth=1):
    all_hypon = list(root_syn.closure(
        lambda s: s.hyponyms(), depth=depth))
    # creates a dictionary like
    # {Synset('hypothesis.n.02'): 0.005906564752148317, Synset('quantity.n.03'): 0.0075294222323759}
 # k=hypon, v=weighted cosine similarity  between definitions corpus and hypon definition
 # the weight is normalized frequency of genus in corpus
 # hypon_corpus is the merge of the hyponyn definition and examples
    hypon_analisys_list = []
    for hypon in all_hypon:
      corpus_to_analyze = []
      preprocessed_defs = preprocess(
          hypon.definition()) if execution_parms["definition_similarity"] else[]
      preprocessed_examples = list(itertools.chain(
          *[preprocess(example) for example in hypon.examples()]))if execution_parms["examples_similarity"] else []
      lemmas_corpus = [lemma.name() for lemma in hypon.lemmas()
                                ] if execution_parms["lemmas_similarity"] else []
      corpus_to_analyze.extend(preprocessed_defs)
      corpus_to_analyze.extend(preprocessed_examples)
      corpus_to_analyze.extend(lemmas_corpus)

      target_corpus_lemmas = [lemma.name() for lemma in list(itertools.chain(
          *[genus_syn.lemmas() for genus_syn in concept.get_genus_bag()]))] if execution_parms["lemmas_similarity"] else []

      target_corpus = concept.get_preprocessed_corpus()
      target_corpus.extend(target_corpus_lemmas)


      hypon_analisys_list.append((hypon, cos_similarity(
          corpus_to_analyze, target_corpus) * genus_weight))

    # return the result omitting the ones with 0 similarity
    return [tuple for tuple in hypon_analisys_list if tuple[0]]


def cos_similarity(sentence_1, sentence_2):
    if (len(sentence_1) == 0 or len(sentence_2) == 0):
        return 0.0
    if (len(sentence_1) == 0 and len(sentence_2) == 0):
        return 1.0
    X_set={w[0] for w in sentence_1}
    Y_set={w[0] for w in sentence_2}
    l1=[]
    l2=[]
    # form a set containing keywords of both strings
    rvector=X_set.union(Y_set)

    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c=0

    # cosine formula
    for i in range(len(rvector)):
        c += l1[i]*l2[i]
    return c / float((sum(l1)*sum(l2))**0.5)


verbs = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

execution_parms={}
if __name__ == "__main__":

  for execution_item in experiments_parameters[8:9]:
    execution_parms = execution_item

    concept_definitions_dict = load_data(
        "./part3/exercise2/input/content-to-form.csv")

    result = "\n\tid\t(genus->hypo)\t\t(genus->hype->hypo)\n"+"\n".join([findConcept(concept)
                                                                          for concept in concept_definitions_dict.values()])
    print("\n".join("{}\t{}".format(k, v) for k, v in execution_parms.items())+result)
    text_file = open("./part3/exercise2/reports/" + execution_parms['test_id'] + ".csv", "w")
    text_file.write(result)
    text_file.close()

   # print("\nGenus Hyper")
   # genus_hyper(concept_definitions_dict)

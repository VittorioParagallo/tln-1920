import sys
from pathlib import Path
import os.path
from tqdm import tqdm
import glob
import filecmp
import csv
import heapq
from nltk.corpus import stopwords
import nltk
from nltk.tokenize import RegexpTokenizer

stop_words = set(stopwords.words('english'))
no_punct_tokenizer = RegexpTokenizer(r'\w+')
wnl = nltk.WordNetLemmatizer()

def create_context(text, nasari):
    """
    It creates a list of Nasari vectors (a list of {term:score}). Every vector
    represents one text term.
    :param text: the list of text's terms
    :param nasari: Nasari dictionary
    :return: list of Nasari's vectors.
    """
    #preprocess
    tokens = {wnl.lemmatize(token) for token
              in no_punct_tokenizer.tokenize(text.lower())
              if token not in stop_words}

    return [nasari[word] for word in (tokens & nasari.keys())]

def weighted_overlap(topic_nasari_vector, paragraph_nasari_vector):
    """
    Implementation of the Weighted Overlap metrics (Pilehvar et al.)
    :param topic_nasari_vector: Nasari vector representing the topic
    :param paragraph_nasari_vector: Nasari vector representing the paragraph
    :return: square-rooted Weighted Overlap if exist, 0 otherwise.
    """
    #function to get item rank in nasari dictionary as key index+1
    item_rank = lambda item, nasari_dict: list(nasari_dict.keys()).index(item) + 1
    
    overlap_keys = list(topic_nasari_vector.keys() & paragraph_nasari_vector.keys())

    if len(overlap_keys) > 0:
        # sum 1/(rank() + rank())
        den = sum(1 / (item_rank(q, topic_nasari_vector) +
                       item_rank(q, paragraph_nasari_vector)) for q in overlap_keys)
        # sum 1/(2*i), 
        num = sum(list(
                            map(lambda x: 1 / (2 * x),
                                   list(range(1, len(overlap_keys) + 1)))))
        return num/den
    return 0

def parse_nasari_dictionary():
    """
    It parse the Nasari input file, and it converts into a more convenient
    Python dictionary.
    :return: a dictionary representing the Nasari input file. Fomat: {word: {term:score}}
    """
    nasari_dict = {}
    reader = csv.reader(open('./part2/exercise3/input/dd-small-nasari-15.txt', "r", encoding="utf-8"), delimiter=';')    
    for line in reader:
      vector_dict = {}
      for term_value in line[2:]:
          term, *value = term_value.split("_")
          vector_dict[term] = value[0] if value else None
      nasari_dict[line[1].lower()] = vector_dict
    return nasari_dict

def summarization(document, nasari_dict, percentage):
    """
    Applies summarization to the given document, with the given percentage.
    :param document: the input document
    :param nasari_dict: Nasari dictionary
    :param percentage: reduction percentage
    :return: the summarization of the given document.
    """

    # getting the topics based on the document's title.
    topic_vecs = create_context(document[0], nasari_dict)

    paragraphs = []
    # for each paragraph, except the title (document[0])
    for index, paragraph in enumerate(document[1:]):
        paragraph_vecs = create_context(paragraph, nasari_dict)

        paragraph_wo = 0  # Weighted Overlap average inside the paragraph.
        
        for paragraph_vec in paragraph_vecs:
            # Computing the sum of WO of all topic_vectors vs paragraph_vector
            paragraph_vec_vs_topic_wo_avg =sum(weighted_overlap(paragraph_vec, topic_vec) / len(topic_vecs)
                           for topic_vec in topic_vecs)         
            # Sum all words WO in the paragraph's WO
            paragraph_wo += paragraph_vec_vs_topic_wo_avg/ len(paragraph_vecs)

        if len(paragraph_vecs) > 0:
            # append in paragraphs a tuple with the index of the paragraph (to
            # preserve order), he WO of the paragraph and the paragraph's text.
            paragraphs.append((index-1, paragraph_wo, paragraph))

    reduced_lenght = round(len(paragraphs)/100*(100-percentage))

    # filter only first n max paragraph and get only text
    new_document = [paragraph[2] for paragraph in paragraphs
                     if paragraph in heapq.nlargest(
                         reduced_lenght, paragraphs, key=lambda x: x[1])]

    return[document[0]] + new_document

def parse_document(file):
    """
    It parse the given document.
    :param file: input document
    :return: a list of all document's paragraph.
    """
    lines = file.read_text(encoding='utf-8').split('\n')
    # If the "#" character is present, it means the line contains the
    # document original link. So, if the # is not present,
    # we have a normal paragraph to append to the list.
    return [line for line in lines if line != '' and '#' not in line]

if __name__ == "__main__":

  percentage= 10
  nasari_dict = parse_nasari_dictionary()

  # Inspecting the input files
  files_documents = Path(
      './part2/exercise3/input/text-documents/').glob('*.txt')

  for file in files_documents:
      document = parse_document(file)
      # For each document do summarization.
      sum_document = summarization(document, nasari_dict, percentage)
      with open('./part2/exercise3/output/' + str(percentage) + '-' + file.name,
                'w', encoding='utf-8') as out_summarized:
          for paragraph in sum_document:
              out_summarized.write(paragraph + '\n')

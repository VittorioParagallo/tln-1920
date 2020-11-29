from random import choice
import csv
import nltk
from nltk.corpus import semcor
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import random
#uncomment only to download first time
#nltk.download('wordnet')
#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('semcor')
tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('english'))


def lesk_algorithm(word, context):
    # intersection of 2 context to compute the overlap
    compute_overlap= lambda ctx1, ctx2: len(set(ctx1) & set(ctx2))
    # get the signature of a sense as definition+examples
    sense_details= lambda syn: preprocess(
        syn.definition() + ' '.join(syn.examples()))
    
    # for each possible word_sense  computes the overlap with context
    # and return the one with max value
    best_sense = max(
        [(sense, compute_overlap(sense_details(sense), context))
         for sense in wn.synsets(word, 'n')],
        key=lambda x: x[1],
        default=None)
    return best_sense[0] if best_sense is not None else None


def preprocess(definition):
    """
    It does some preprocess: removes the stopword and punctuation
    :param definition: a string representing a definition
    :return: a set of string which contains the preprocessed string tokens.    """
    return [token for token
            in tokenizer.tokenize(definition.lower())
            if token not in stop_words]


def lexsnKey2Syn(sensekey):
  '''
  Returns the sense from the sense key ex. person%1:03:00::

  Sense Key Encoding
  This is preferred by Princeton WN, described in WordNet's sense index Man Page
  A sense is encoded in three parts: lemma, pos, sense number (in the corpus wn_lemma, lexsn, wn).

  lex_sense (lexsn) = ss_type:lex_filenum:lex_id:head_word:head_id 
  sense number (wn)
  - lemma is the text of the word or collocation as found in the WordNet database index file corresponding to pos. It shold be in lower case, and collocations are formed by joining individual words with an underscore (_) character.
  - ss_type is a one digit decimal integer representing the synset type for the sense.
          ╔══╦══╦═══════╗
          | In  | POS | Part of Speech |
          |══|═══|════════|
          |  1  |   n    | NOUN             | 
          |══|═══|════════|
          |  2  |   v    | VERB              |
          |══|═══|════════|
          |  3  |   a    | ADJECTIVE      |
          |══|═══|════════|
          |  4  |   r    | ADVERB          |
          |══|═══|════════|
          |  5  |   s    | ADJ SATE        |
          ╚═════╩═══════╝
    - lex_filenum is a two digit decimal integer representing the name of the lexicographer file containing the synset for the sense. See lexnames(5WN) for the list of lexicographer file names and their corresponding numbers.
    - lex_id is a two digit decimal integer that, when appended onto lemma , uniquely identifies a sense within a lexicographer file. lex_id numbers usually start with 00 , and are incremented as additional senses of the word are added to the same file, although there is no requirement that the numbers be consecutive or begin with 00 . Note that a value of 00 is the default, and therefore is not present in lexicographer files. Only non-default lex_id values must be explicitly assigned in lexicographer files. See wninput(5WN) for information on the format of lexicographer files.
    - head_word is only present if the sense is in an adjective satellite synset. It is the lemma of the first word of the satellite's head synset.
    - head_id is a two digit decimal integer that, when appended onto head_word , uniquely identifies the sense of head_word within a lexicographer file, as described for lex_id. There is a value in this field only if head_word is present.
  Concatenating the lemma and lex_sense fields of a semantically tagged word, using % as the concatenation character, creates the sense_key for that sense, which can in turn be used to search the sense index file.
  According to PWN, a sense_key is the best way to represent a sense in semantic tagging or other systems that refer to WordNet senses. sense_keys are independent of WordNet sense numbers and synset_offsets, which vary between versions of the database. Using the sense index and a sense_key the corresponding synset (via the synset_offset) and WordNet sense number can easily be obtained.
  Code to go from lemma, sense_key, sense_no to synset using nltk
  '''
  # sensekey like  sc2ss('person%1:03:00::')

  return wn.lemma_from_key(sensekey).synset()


# return a random list of triple (goldSyn, word_to_wsd, text_sent) 
# from the brown corpus
def get_random_sent_goldsyn_brown(quantity):

    sents = semcor.xml('brown2/tagfiles/br-n12.xml').findall('context/p/s')

    # prepare the ranges for the random function
    random_index2explore = list(range(0, len(sents)-1))
    results = []

    # add sentences to the result till the required quantity is reached, or the dataset has no more sentences
    while len(results) < quantity and len(random_index2explore) > 0:
        # choose a random index not previously
        index = choice(random_index2explore)
        random_index2explore.remove(index)
        raw_sent = ''
        # a list of tuple like (word, goldSynset) to choose from
        sent_noun_list = []
        for wordform in sents[index]:
            raw_sent += ' ' + wordform.text
            lemma = wordform.get('lemma')
            lexsn = wordform.get('lexsn')
            wnsn = wordform.get('wnsn')
            if wordform.get('pos') == 'NN' and lemma is not None and lexsn is not None and wnsn != '0' and '_' not in wordform.text:
                sent_noun_list.append(
                    (wordform.text, lexsnKey2Syn(f'{lemma}%{lexsn}')))
        # if the analyzed sentence has nouns one is randomly chosed and assigner to the return sentence
        if len(sent_noun_list) > 0:
            random_gold_syn = random.choice(sent_noun_list)
            results.append((random_gold_syn[1], random_gold_syn[0], raw_sent))
    return results


if __name__ == "__main__":
  # PARTE 1
  reader = csv.reader(open(
      './part2/exercise1/input/sentences.txt', 'r'))
  index = 0
  with open('./part2/exercise1/output/task2_WSD_results.csv', "w") as out:

    for line in reader:
        if len(line) > 0 and line[0][0] == '-':
            term = line[0].split('**')[1]
            definition = preprocess(line[0])
            out.write('\n{}\n{} - {}'.format(index, term, definition))
            wsd_sense = lesk_algorithm(term, definition)
            out.write(f'\nLesk Sense {wsd_sense}: {wsd_sense.definition()}')
            out.write(f'\nOriginal sentence: {line}')
            out.write(
                f"\nSentence with sinonyms: {line[0].split('**')[0]} {[lemma.name() for lemma in wsd_sense.lemmas()]} {line[0].split('**')[2]}\n\n")
            index += 1
    out.close()

  # PARTE 2
  # list of triples(goldSyn, word_to_wsd, text_sent)
  quantity_of_sents =50
  sentences = get_random_sent_goldsyn_brown(quantity_of_sents)

  acc_score = 0
  unfound_syns = []
  with open('./part2/exercise1/output/task2_SemCor_results.csv', "w") as out:
    for sent in sentences:
        wsd_syn = lesk_algorithm(sent[1], preprocess(sent[2]))
        if wsd_syn is None:
          unfound_syns.append(sent)
        else:
          out.write('\n{}\n{}\n{}  vs. {}\n'.format(
              sent[1], sent[2], wsd_syn, sent[0]))
          acc_score += 1 if wsd_syn == sent[0] else 0
    out.write('\nUnfound syns:\n {}'.format(unfound_syns))
    out.write('\n\nAccuracy {}/{}'.format(acc_score, len(sentences)))

import re
import csv
import nltk
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet as wn
import itertools
import re
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

no_punct_tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('english'))

def flat_list(list_of_lists): return list(itertools.chain(*list_of_lists))


def preprocess(text):
    """
    It does some preprocess: removes the stopword and punctuation
    :param definition: a string representing a definition
    :return: a set of string which contains the preprocessed string tokens.    """
    return ' '.join([token for token
            in no_punct_tokenizer.tokenize(text.replace('_', ' ').lower())
            if token not in stop_words])

def get_main_clause(frame_name):
    """
    Get of the main clause from the frame name (in italian "reggente").
    :param frame_name: the name of the frame
    :return: the main clause inside the frame name
    """
    tokens = nltk.word_tokenize(frame_name.replace('_', ' '))
    for elem in reversed(nltk.pos_tag(tokens)):
        if elem[1] in ["NN", "NNS"]:
            return elem[0] 

#a wordnet pos like v,n,a or s can be passed to filter synsets
def get_wn_ctx(word, pos=None):
    """
    :param word: word for which we need to find meaning
    :return: a dictionary of Synset and relative ctx associated to the given word
    """

    word = word.replace(' ', '_')
    synsets = wn.synsets(word)
    if len(synsets) < 1:
      synsets = wn.synsets(word.replace('_', ''))
    if len(synsets) < 1:
      synsets = wn.synsets(get_main_clause(word))
    if len(synsets) < 1:
      print('!!! No wn_synset found for word: '+word)
    
    if pos in ['n', 'v', 'a', 's', 'r']:
      synsets = filter(lambda syn: syn.pos() == pos, synsets)

    result = {}
    for syn in synsets:
      syn_ctx = [syn.definition()] + syn.examples() + syn.lemma_names() + \
                      flat_list([
                                hypo.examples() + hypo.lemma_names() + [hypo.definition()]
                                  for hypo in syn.hyponyms()]) + \
                      flat_list([
                                hype.examples() + hype.lemma_names() + [hype.definition()]
                                  for hype in syn.hypernyms()])
                
      result[syn.name()] = syn_ctx
    return result

def bag_of_words(ctx_fn, ctx_wn):
    """
    Givent the framenet context ctx_fn and a the wordnet context as a dictionary of values <-> candidate synsets
    return the best synset
    :param ctx_fn: the first disambiguation context (from Framenet)
    :param ctx_wn: the second disambiguation context (from Wordnet)
    :return: the synset with the highest score
    """
    def compute_score(ctx1, ctx2): return len(set(ctx1) & set(ctx2)) + 1
    
    fn_words_bag = set(no_punct_tokenizer.tokenize(
        ' '.join([
            ''.join(preprocess(data)) for data in ctx_fn if data is not None])))

    sense_score_list = [(sense, compute_score(
                                            set(no_punct_tokenizer.tokenize(
                                              ' '.join(
                                                  [''.join(preprocess(data)) for data in ctx_wn[sense] if data is not None]))),
                                            fn_words_bag))
                                  for sense in ctx_wn]
    return max(sense_score_list, key=lambda x: x[1],default=[None])[0]


if __name__ == "__main__":

    # frame_ids = [8, 2286, 2246, 1490, !2582] Paragallo
    # frame_ids = [!1303, 2076, 56, 723, !710] paragallo
    # frame_ids = [1071, 1083, 1017, 2625, 731] PARAGALLO

    # getFrameSetForStudent('PARAGALLO')
    # student: PARAGALLO
    # ID: 1071	frame: People_by_vocation  (vocation)
    # ID: 1083	frame: Subjective_influence (influence)
    # ID: 1017	frame: Noise_makers (makers) attenzione esiste noisemakers
    # ID: 2625	frame: Relational_location (location)
    # ID:  731	frame: Becoming_silent (silent)
    
    #get the frames
    frames =[ fn.frame_by_id(id) for id in [1071, 1083, 1017, 2625, 731]]
    
    #get the golden data
    reader = csv.DictReader(
        open('./part2/exercise2/input/gold.txt'), delimiter='\t')
    #row={'FrameId': '1071', 'name': 'People_by_vocation', 'sense': 'career.n.01', 'type': 'name'}
    gold_data = [row for row in reader]


    with open('./part2/exercise2/output/results.csv', "w", encoding="utf-8") as out:

      row_template = '{}\t{}\t{}\t{}\t{}\t{}\n'
      out.write(row_template.format('FrameId','type','name','sense','gold','score'))
      
      #function to find the gold syn in file
      find_gold_syn = lambda fId, type, name:next(gold['sense']
                                                  for gold in gold_data
                                                  if gold["FrameId"] == str(fId) and gold["type"] == type and gold["name"] == name.replace(' ', '_'))
                                                  
      scores=[]
      for f in frames:
        #crea contesti di disambiguazione per frame
        ctx_f_fn = [ f.definition]+re.split(', |_|-|()-!', f.name)  
        ctx_f_wn = get_wn_ctx(f.name)
        sense_name = bag_of_words(ctx_f_fn, ctx_f_wn)
        
        #cerca gold syn e valuta lo score
        gold_fname_syn = find_gold_syn(f.ID,'name', f.name)
        scores.append( int(gold_fname_syn == sense_name))

        # salva i risultati
        out.write(row_template.format(
            f.ID, 'name', f.name, sense_name, gold_fname_syn, scores[-1]))

        for key in f.FE:
          ctx_fe_fn = [key, f.FE[key].definition]
          ctx_fe_wn = get_wn_ctx(key)
          sense_fe = bag_of_words(ctx_fe_fn, ctx_fe_wn)
          
          gold_fe_syn = find_gold_syn(f.ID, 'FE', key)
          scores.append(int(gold_fe_syn == sense_fe))

          out.write(row_template.format(
              f.ID, 'FE', key, sense_fe, gold_fe_syn, scores[-1]))

        for lu in f.lexUnit.values():
          lu_word, lu_pos = lu.name.split('.')

          ctx_lu_fn = [lu_word, lu.definition]
          ctx_lu_wn = get_wn_ctx(lu_word, lu_pos)
          sense_lu = bag_of_words(ctx_lu_fn, ctx_lu_wn)

          gold_lu_syn = find_gold_syn(f.ID, 'LU', lu.name)
          scores.append(int(gold_lu_syn == sense_lu))

          out.write(row_template.format(
              f.ID, 'LU', lu.name, sense_lu, gold_lu_syn, scores[-1]))

      total_score = sum(scores)
      count=len(scores)
      out.write(
                  '\nACCURACY: {}/{} ({:.2f}%)'.format(total_score, count, total_score/count*100))
      print('\nACCURACY: {}/{} ({:.2f}%)'.format(total_score,
                                                         count, total_score / count * 100))
  

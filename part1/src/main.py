import nltk
from nltk.corpus import wordnet as wn
from nltk import word_tokenize
#eseguire solo una vollta
#nltk.download('wordnet')
#nltk.download('omw')

from translate import Translator

#spaCy import
import it_core_news_sm
import it_core_news_md
#python3 -m spacy download it_core_news_lg
import it_core_news_lg
from spacy import displacy

#plot trees
from nltk.tree import Tree

#simpleNLG
from simplenlg import NLGFactory, Realiser, SPhraseSpec, LexicalCategory, LexicalFeature, PhraseCategory, Feature, Form, Tense, NumberAgreement, InterrogativeType
from simplenlg.lexicon import Lexicon
from nltk.wsd import lesk

from collections import Counter
from switch import Switch
from sintatic_node import SintaticNode
lexPosMapper = dict(ADJ='a', ADV='r', NOUN='n', VERB='v', AUX='v', DET='det')
def translate_lemma_it_en(lemma, spaCy_pos):
    """
    Function for 1:1 translate.

    :param lemma: lemma to translate
    :param penn_pos: the tagged spacy pos can be ADJ, ADJ_SAT, ADV, NOUN, VERB -> "a", "s", "r", "n", "v"
    :return: the english translation of the italian word
    """
    #verifica se è ha un pos che è possibile tradurre con wordnet
    wordNetPos = lexPosMapper.get(spaCy_pos)

    if wordNetPos == None:
         syns = wn.synsets(lemma, lang="ita")
    else:
         syns = wn.synsets(lemma, wordNetPos, lang="ita")
    #Tests 
    #cane_lemmas = wn.lemmas("potere", "v", lang="ita")
    #print([(w.name(), w.synset().lex_id(), w.synset().name().partition('.')[0], w.synset().lexname(), w.synset().pos())for w in cane_lemmas])
     # lemmas = wn.lemmas(lemma, wordNetPos, lang="ita")
     # if len(lemmas)>0:
     #   return lemmas[0].synset().name().partition('.')[0]
    if len(syns) > 0:
        return Counter([s.name().partition('.')[0] for s in syns]).most_common(1)[0][0]
        #syn=lesk(word_tokenize(sent),lemma, synsets=syns)
        #return syn.name().partition('.')[0]
    else:
        return Translator(from_lang="italian", to_lang="english").translate(lemma).replace('.','')
        print(lemma+':'+spaCy_pos+' not found in word net')
        return None


def preprocessing(node_dict):
  #unisci i digrammi per evitare i compound
    compoundNodeList = list(filter(lambda elem:
                      elem[1].get_dependency() == 'compound', node_dict.items()))
    if (len(compoundNodeList) > 0):
      compoundNode = compoundNodeList.__next__()[1]
      headNode = node_dict[compoundNode.get_head_id()]
      headNode.set_lemma_eng(compoundNode.get_lemma_eng() + ' ' + headNode.get_lemma_eng())
      node_dict[headNode.get_id()] = headNode
      #TEORICAMENTE DOVREBBE ESSERE SUFFICIENTE UNIRE I DUE NOUN PERCHé HANNO LE STESSE
      #CARATTERISTICHE IN QUANTO COMPOUND, MA NEL CASO DELLA SPADA LASER SPADA POTREBBE ESSERE
      #PLURALE, NON è veramente un compound anzi dovrebbe essere aggettivo

      #aggiorniamo i puntatori dei figli per puntare al nuovo head e non più al compound
      children = list(filter(lambda x: (x.get_head_id() ==
                                        compoundNode.get_id()), list(node_dict.values())))
      for child in children:
        child.set_head_id(headNode.get_id())
        node_dict[child.get_id()] = headNode

      #eliminiamo il compound dal dizionario
      my_dict.pop(compoundNode.get_id(), None)

      #rilanciamo ricorsivamente alla ricerca di altri compound
      return preprocessing(node_dict)
    else:
      return node_dict


def parsePhraseNode(node_dict, node):
  #SE IL NODO è ROOT inizializzare  sPhraseSpec
  if node.get_dependency() == 'ROOT':
    sPhraseSpec = nlg_factory.createClause()


  #Analizza il nodo
  print('___________________________________')
  print('ANALIZZANDO IL NODO')
  print('_________________')
  print('|\t'+str(node.get_id())+'\t|')
  print('-----------------')
  print(str(node))

  with Switch(node.get_pos()) as case:



      if case( 'VERB'):
        phrase = nlg_factory.createVerbPhrase()
        phrase.setVerb(node.get_lemma_eng())

        verbSintax = dict(x.split("=") for x in node.get_sintax()[3:].split("|"))
        if verbSintax.get('Tense') == 'Past' and verbSintax.get('VerbForm') == 'Part':
          phrase.setFeature(Feature.FORM, Form.PAST_PARTICIPLE)

      if case('AUX'):
        phrase = nlg_factory.createVerbPhrase()
        phrase.setVerb(node.get_lemma_eng())

        verbSintax = dict(x.split("=")
                          for x in node.get_sintax()[3:].split("|"))
        if verbSintax.get('Tense') == 'Past' and verbSintax.get('VerbForm') == 'Part':
          phrase.setFeature(Feature.FORM, Form.PAST_PARTICIPLE)

      if case('NOUN'):
       phrase = nlg_factory.createNounPhrase()
       phrase.setNoun(node.get_lemma_eng())
       nounSintax = dict(x.split("=")
                         for x in node.get_sintax()[3:].split("|"))
       if nounSintax.get('Number') == 'Plur':
         phrase.setFeature(Feature.NUMBER, NumberAgreement.PLURAL)

      if case('PROPN'):
       phrase = nlg_factory.createNounPhrase()
       phrase.setNoun(node.get_lemma_eng())


      if case('X'):
       phrase = nlg_factory.createNounPhrase()
       phrase.setNoun(node.get_lemma_eng())

      if case('ADJ'):
       phrase = nlg_factory.createAdjectivePhrase()
       phrase.setAdjective(node.get_lemma_eng())



  isPP=False
  #Analizza i figli
  children = list(filter(lambda x: (x.get_head_id() == node.get_id()), list(node_dict.values())))
  print('-----------I dipendenti sono:')
  print('\n'.join([str(child) for child in children]))
  for child in children:
      with Switch(child.get_dependency()) as case:
        if case('obj'):
            phrase.setObject(parsePhraseNode(node_dict, child))

        #if case('aux'):
        if case('det'):
            if len(list(filter(lambda x: x.get_dependency() == 'nmod', children)))<1:
             phrase.setDeterminer(child.get_lemma_eng())

        if case('amod'):
            phrase.addPreModifier(parsePhraseNode(node_dict, child))

        if case('cop'):
            if node.get_dependency() == 'ROOT':
              sPhraseSpec.setVerb(child.get_lemma_eng())

        if case('advmod'):
            phrase.addPostModifier(child.get_lemma_eng())
        
        if case('aux:pass'):
          phrase.setFeature(Feature.PASSIVE, True)

        if case('aux'):  
          verbSintax = dict(x.split("=")
                            for x in child.get_sintax()[3:].split("|"))
          
          if verbSintax.get('Tense') == 'Pres' and phrase.getFeature(Feature.FORM) == Form.PAST_PARTICIPLE:
              phrase.setFeature(Feature.TENSE, Tense.PRESENT)
              phrase.setFeature(Feature.FORM, Form.NORMAL)
              phrase.setFeature(Feature.PERFECT, True)

        if case('nmod'):
            returnPhrase = parsePhraseNode(node_dict, child)
            if node.get_dependency() == 'ROOT':
              sPhraseSpec.setIndirectObject(returnPhrase)
              if returnPhrase.getCategory() == PhraseCategory.PREPOSITIONAL_PHRASE:
                #Migliorare questa parte per Genitivo sassone Es. verificare che nel returnPhrase c'è det:poss
                returnPhrase.setPostModifier(phrase)
            else:          
                if returnPhrase.getCategory() == PhraseCategory.PREPOSITIONAL_PHRASE:
                  phrase.setPostModifier(returnPhrase)


        if case('nsubj:pass'):
            if node.get_dependency() == 'ROOT':
              sPhraseSpec.setSubject(parsePhraseNode(node_dict, child))
             # sPhraseSpec.setFeature(Feature.PASSIVE, True)
              returnPhrase = parsePhraseNode(node_dict, child)

        if case('nsubj'):
            if node.get_dependency() == 'ROOT':
              sPhraseSpec.setSubject(parsePhraseNode(node_dict, child))
            else:
              phrase.setSubject(parsePhraseNode(node_dict, child))
          
        if case('obl'):
            if node.get_dependency() == 'ROOT':
              sPhraseSpec.setObject(parsePhraseNode(node_dict, child))
            else:
              phrase.setObject(parsePhraseNode(node_dict, child))             

        if case('det:poss'):
            detPoss2persPron = {'my': 'I', 'mine': 'I', 'your': 'you', 'yours':'you','his': 'he',
                                'her': 'she', 'hers': 'she', 'its': 'it', 'our': 'we', 'ours':'we', 'their': 'they','theirs':'they', "one's": 'one'}
            possPron = nlg_factory.createWord(detPoss2persPron[child.get_lemma_eng()], LexicalCategory.PRONOUN)
            possPron.setFeature(Feature.POSSESSIVE, True)
            phrase.setFeature(Feature.POSSESSIVE, True)
            phrase.setSpecifier(possPron)


        if case('case'):
            isPP=True
            pp = nlg_factory.createPrepositionPhrase()
            detPossBrotherNodes = list(
                filter(lambda x: x.get_dependency() == 'det:poss', children))
            if len(detPossBrotherNodes) < 1:
                pp.setPreposition(child.get_lemma_eng())

     

        if case.default:
            print('ATTENZIONE NESSUNA OPERAZIONE PER LA DIPENDENZA:' +
                  child.get_dependency())
 
  if isPP:
        pp.addComplement(phrase)
        phrase = pp
        
  if node.get_dependency() == 'ROOT' and phrase.getCategory()==PhraseCategory.VERB_PHRASE:
      sPhraseSpec.setVerb(phrase)
  if node.get_dependency() == 'ROOT' and phrase.getCategory()==PhraseCategory.ADJECTIVE_PHRASE:
      sPhraseSpec.setObject(phrase)    
  #if node.get_dependency() == 'ROOT' and phrase.getCategory()==PhraseCategory.NOUN_PHRASE:
  #    sPhraseSpec.setSubject(phrase)

  if node.get_dependency() == 'ROOT':
    return sPhraseSpec

  return phrase
  print('fine')


def postProcessing(sPhraseSpec, node_dict):
  #verifica punct in caso di interrogative
    questionMarksList = list(filter(lambda elem:
                                    elem.get_dependency() == 'punct' and elem.get_original_token() == '?', node_dict.values()))
    if (len(questionMarksList) > 0):
        sPhraseSpec.setFeature(Feature.INTERROGATIVE_TYPE,
                               InterrogativeType.YES_NO)
        print(str(len(questionMarksList)))
  #POST PROCESSING IN CASO IN CUI IL SOGGETTO NON SIA STATO ESPLICITATO
    if sPhraseSpec.getSubject() == None:
      #sPhraseSpec.setFeature(LexicalFeature.EXPLETIVE_SUBJECT, True)
      verbalPhrase = sPhraseSpec.getVerbPhrase()
      allFeatures = verbalPhrase.getAllFeatures()
      with Switch(str(verbalPhrase.getFeature(Feature.PERSON))) as case:
        if case('FIRST'):
           sPhraseSpec.setSubject('I') if str(verbalPhrase.getFeature(
               Feature.NUMBER)) == 'SINGULAR' else sPhraseSpec.setSubject('we')
        if case('SECOND'):
          str(verbalPhrase.getFeature(LexicalFeature.GENDER))
        if case('THIRD'):
            if str(verbalPhrase.getFeature(Feature.NUMBER)) != 'SINGULAR':
              sPhraseSpec.setSubject('they')
            else:  # TODO verificare genere
              if verbalPhrase.getFeature(LexicalFeature.GENDER)==None:
               sPhraseSpec.setSubject('it')
              else:
               sPhraseSpec.setSubject('he')
    return sPhraseSpec

if __name__ == "__main__":
  
    sentences = [
      "è la spada laser di tuo padre",
                 "Ha fatto una mossa leale",
                 "Gli ultimi avanzi della vecchia Repubblica sono stati spazzati via",
                 "Paolo ama Francesca",
                 "Paolo ama Francesca?",
                "Paolo ama Francesca infinitamente",
                 "Paolo ama Francesca dolcemente",
                 "Lucia corre",
                 "Lucia corre?",
                 "La vita è bella.",
                 "Il gatto è sul tavolo",
                 "Il gatto blu salta sul tavolo agilmente",
                 "Il gatto di mio cugino salta sul tavolo agilmente",
          #       "Il gatto blu di mio cugino salta sul tavolo agilmente",
                 "Il ricordo di tuo padre è ancora vivo",
                  "Marco è stato arrestato",
                  "Un amico di un mio amico è stato arrestato", #Ancora problemi di genitivo sassone
                  "La linguistica computazionale è complicata",
                  "I diamanti sono molto costosi",
        "Il lavoro di Vittorio è stato completato",
                 ]
                 
    sentences1 = [
    "è la spada laser di tuo padre"]
###PRIMI TEST CON NLTK
#    my_grammar = nltk.data.load( 'file:///Users/darka/Desktop/tln_repo/tln-1920/part1_A/input/my-grammar.fcfg')
#  parser = parse.load_parser( '/Users/darka/Desktop/tln_repo/tln-1920/part1_A/input/my-grammar.fcfg ')
    
   # parser = nltk.ChartParser(my_grammar)
   # tokens = nltk.word_tokenize("Gli ultimi avanzi della vecchia Repubblica sono stati spazzati via")
  #  for tree in parser.parse(tokens):
  # for tree in parser.parse(list(map(lambda x: x.lower(), "Gli ultimi avanzi della vecchia Repubblica sono stati spazzati via".split()))):
 #     print(tree)
 #     tree.draw()
   # tokens = "è la spada laser di tuo padre".split()
   # trees = parser.parse(tokens)
   # print(data)

    translantions=[]
    nlp = it_core_news_md.load()
    for sent in sentences:
        doc = nlp(sent)
        #displacy.serve(doc, style='dep')

        #tupla contenente: l'indice del token nel testo, il Pos,,il testo del token,  il tag morfosintattico l'indice del token padre, il tag di dipendenza,
        #print([(w.i, w.pos_, w.text, w.lemma_, translate_lemma_it_en(w.lemma_, w.pos_), w.head.i,  w.dep_,  w.tag_) for w in doc])
        
        node_dict ={}
        for w in doc:
          wordNode = SintaticNode()
          wordNode.set_id(w.i)
          wordNode.set_pos(w.pos_)
          wordNode.set_original_token(w.text)
          wordNode.set_lemma_ita(w.lemma_)
          wordNode.set_lemma_eng(translate_lemma_it_en(w.lemma_, w.pos_))
          #PER EVITARE IL LOOP INFINITO DURANTE LA RICORSIONE ELIMINIAMO IL PUNTATORE A SE STESSO DEL ROOT
          wordNode.set_head_id(w.head.i if w.dep_!='ROOT' else None)
          wordNode.set_dependency(w.dep_)
          wordNode.set_sintax(w.tag_)
          node_dict[w.i] = wordNode
          print("Created node:\n" + str(wordNode))
        
          node_dict =preprocessing(node_dict)
        #rootNode = ({key: value for (key, value) in node_dict.items() if value.get_dependency() == 'ROOT'}).pop(1)
        rootNode = filter(lambda elem: 
                              elem[1].get_dependency() == 'ROOT', node_dict.items()).__next__()[1]

        print("The root Node is:\n" + str(rootNode))

      #NLG 
        lexicon = Lexicon.getDefaultLexicon()
        nlg_factory = NLGFactory(lexicon)
        realiser = Realiser(lexicon)
        


        sPhraseSpec=  parsePhraseNode(node_dict, rootNode)
        
        translated = realiser.realiseSentence(
            postProcessing(sPhraseSpec, node_dict))
        translantions.append(translated)
        print(translated)

    print('________________RISULTATI_________________')
    for original, translated in zip(sentences, translantions):
      print(original + ' -> ' + translated)

    
  

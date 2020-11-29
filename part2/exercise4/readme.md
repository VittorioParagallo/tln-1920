# Sense identification

Given a set of couple of words, manually score the similarity in a range [0-4] as by specification:
```
4: Very similar -- The two words are synonyms (e.g., midday-noon).
3: Similar --The two words share many of the important ideas of their meaning but include slightly different details.They refer to similar but not identical concepts (e.g., lion- zebra).
2: Slightly similar -- The two words do not have a ver y similar meaning, but share a common topic/domain/function and ideas or concepts that are related (e.g., >house-window).
1: Dissimilar -- The two items describe clearly dissimilar concepts, but may share some small details, a far relationship or a domain in common and might be >likely to be found together in a longer document on the same topic (e.g., software-keyboard).
0: Totally dissimilar and unrelated -- The two items do not mean the same thing and are not on the same topic (e.g., pencil-frog).
```

Then in a first step compute the similarity with nasary embenddings and evaluate the the results  with manually annotated values. In a second step get the source sences getting the previously computed similarity values.

### Input
The input data have been retrieved from the file it.test.data.txt according to the result of the function get_range('Paragallo') in. file semeval_mapper.ipynb. The input range is 
```
Paragallo: coppie nell'intervallo 301-350
```
These data have been stored in the file 1st_task_50_couples_manually_annotated.tsv and manually annotated. (The same file is also in output folder because the annotation is the result of first part of exercise4)

Here is the table with manual annotation:
| Word 1                                 | Word 2                | manual annotation |
|----------------------------------------|-----------------------|-------------------|
| disturbo bipolare                      | problema              | 2.50              |
| acido                                  | base                  | 3.00              |
| zero assoluto                          | vapore                | 2.80              |
| rivoluzione verde                      | vernice               | 0.80              |
| sistema operativo                      | deep learning         | 3.00              |
| olimpiadi internazionali di matematica | teoria                | 1.60              |
| El Niño                                | equatore              | 2.50              |
| distintivo                             | vetro                 | 0.30              |
| dimora                                 | scultore              | 0.60              |
| atmosfera                              | ozono                 | 3.44              |
| scudo                                  | brocchiero            | 4.00              |
| moneta                                 | pagamento             | 3.50              |
| avena                                  | campo                 | 3.50              |
| monaco                                 | croce                 | 3.00              |
| cannoniera                             | costa                 | 2.00              |
| roccia                                 | miniera               | 3.00              |
| leggenda                               | morale                | 2.70              |
| campione                               | vincitore             | 3.00              |
| dado                                   | cubo                  | 3.70              |
| topologia                              | struttura             | 3.50              |
| cappella                               | cavo                  | 0.20              |
| flusso di cassa                        | fiume                 | 1.00              |
| serial killer                          | assassino             | 3.90              |
| matrice                                | molecola              | 3.00              |
| moda                                   | stile                 | 2.50              |
| vessillologia                          | bandiera              | 3.00              |
| trattato di Maastricht                 | Europa                | 3.00              |
| geyser                                 | sorgente              | 2.80              |
| saccarosio                             | carboidrato           | 3.00              |
| spiaggia                               | costa                 | 3.00              |
| mercato azionario                      | borsa                 | 4.00              |
| tradizione                             | artigianato           | 2.50              |
| romanzo                                | scrittore             | 3.20              |
| panino                                 | Subway                | 3.00              |
| acustica                               | suono                 | 3.50              |
| scherma                                | ginnastica            | 3.00              |
| scrittore                              | regalo                | 0.50              |
| bosco                                  | Tiger Woods           | 0.30              |
| nuvola                                 | finestra              | 2.80              |
| JPEG                                   | PDF                   | 3.40              |
| regista                                | capo                  | 3.50              |
| tassa                                  | Brexit                | 2.00              |
| impollinazione                         | stame                 | 2.50              |
| videogioco                             | gioco per PC          | 4.00              |
| cura                                   | operazione chirurgica | 3.00              |
| risaia                                 | patata                | 2.80              |
| appunti                                | compito               | 3.00              |
| volpe                                  | cellula del sangue    | 0.00              |
| cloruro di sodio                       | sale                  | 4.00              |
| reddito                                | qualità della vita    | 3.20              |

### Output
The first task outputs in the output folder both the manually and computed similarity scores in files:
-  1st_task_50_couples_manually_annotated.tsv
-  1st_task_50_couples_computer_annotated.tsv
the second task instead outpus the file:
- 2nd_task_bnsyns_retrieval.tsv with the original couples, the 2 synsets maximizing the similarity and the first 3 lemmas of each syn
| word1  | word1     | syn1         | syn2         | lemmas_syn1                         | lemmas_syn2                        |
|--------|-----------|--------------|--------------|-------------------------------------|------------------------------------|
| moneta | pagamento | bn:00016448n | bn:00061119n | cash,bancomat,contante              | pagamento,compenso,corresponsione  |
| avena  | campo     | bn:00007439n | bn:00034265n | avena,genere_avena,avena_(botanica) | campagna,campo_(agricoltura),campo |
## Structure
The scrips is exercise4.py archived in the src and includes:
- main in which all the calls are done
- get_synset_terms which calls the Babelnet API and retrieves the senses of a specified word
- parse_nasari parses the nasari text input in 2 dictionaries   
  - {babelId: [nasari vector's values]}
  - {babelID: word_en}
- parse_italian_synset parses the SemEval17_IT_senses2synsets in a dictionary with italian word as key and corresponding babelnet syn ids in values
- parse_input_words retrieves from the file 1st_task_50_couples_manually_annotated the word couples with their manual annotation
- best_sense_couple_by_words is the most important function that given in input two word's list of babelnet synset id and the nasary dictionary returns:
  -  the couple of synset maximizing the cosine similarity 
  -  the cosine similarity score
 ```python
 def best_sense_couple_by_words(bnsn_ids_word1, bnsn_ids_word2, nasari_dict):
    """
    :param bnsn_ids_word1: list of BabelID of the first word
    :param bnsn_ids_word2: list of BabelID of the second word
    :param nasari_dict: NASARI dictionary
    :return: the couple of senses (their BabelID) that maximise the score and
    the cosine similarity score.
    """
    # creates all the combinations of bn_syns1 and bn_syns2 which are present in nasari_dict.keys()
    # for each combination computes the cosine sym and store the list as a triple syn1, syn2, score
    similarities = [(x, y,  cosine_similarity([nasari_dict[x]], [nasari_dict[y]])[0][0])
                            for x in bnsn_ids_word1
                              for y in bnsn_ids_word2
                                 if set([x, y]).issubset(nasari_dict.keys())]
    # find the the couple with max score or returns  (None,None,0)
    max_value = max(similarities, key=lambda x: x[2], default=(None, None, 0))
    return (max_value[0], max_value[1]), max_value[2]

 ```
  
## Results
The overall results are very good (listed after the tables)

**1st_task_50_couples_manually_annotated.tsv:**

| word1                                  | word2                 | nasary_similarity  |
|----------------------------------------|-----------------------|--------------------|
| disturbo bipolare                      | problema              | 1.9378376618677118 |
| acido                                  | base                  | 3.9324214179911223 |
| zero assoluto                          | vapore                | 3.3067882136823696 |
| rivoluzione verde                      | vernice               | 1.6532862975634155 |
| sistema operativo                      | deep learning         | 2.7513306548476186 |
| olimpiadi internazionali di matematica | teoria                | 1.920599025862439  |
| el niño                                | equatore              | 2.694604575762993  |
| distintivo                             | vetro                 | 2.2275793839336004 |
| dimora                                 | scultore              | 1.9299862543457482 |
| atmosfera                              | ozono                 | 3.4429753166150294 |
| scudo                                  | brocchiero            | 4.000000000000001  |
| moneta                                 | pagamento             | 3.6665537892129545 |
| avena                                  | campo                 | 3.171526374551944  |
| monaco                                 | croce                 | 2.883494105217141  |
| cannoniera                             | costa                 | 2.198027978925986  |
| roccia                                 | miniera               | 2.918833736796582  |
| leggenda                               | morale                | 2.380993558960603  |
| campione                               | vincitore             | 2.909419475946923  |
| dado                                   | cubo                  | 4.000000000000001  |
| topologia                              | struttura             | 3.6011211283271667 |
| cappella                               | cavo                  | 3.2873434470640532 |
| flusso di cassa                        | fiume                 | 1.093187695377789  |
| serial killer                          | assassino             | 3.7526252319277615 |
| matrice                                | molecola              | 3.294885565842221  |
| moda                                   | stile                 | 2.4316387764816016 |
| vessillologia                          | bandiera              | 3.9290495008119812 |
| trattato di maastricht                 | europa                | 3.9272900643906423 |
| geyser                                 | sorgente              | 2.7977836009831845 |
| saccarosio                             | carboidrato           | 3.5793411701675537 |
| spiaggia                               | costa                 | 3.6247859753547536 |
| mercato azionario                      | borsa                 | 4.000000000000002  |
| tradizione                             | artigianato           | 2.4591437383671884 |
| romanzo                                | scrittore             | 3.6038960996391944 |
| panino                                 | subway                | 3.118935444943748  |
| acustica                               | suono                 | 3.6993281903289112 |
| scherma                                | ginnastica            | 2.5175215375816755 |
| scrittore                              | regalo                | 1.6633264641512817 |
| bosco                                  | tiger woods           | 2.1503941855314617 |
| nuvola                                 | finestra              | 3.350045378233494  |
| jpeg                                   | pdf                   | 3.1701180384891035 |
| regista                                | capo                  | 3.692612847797404  |
| tassa                                  | brexit                | 1.7950954667568517 |
| impollinazione                         | stame                 | 3.8792874638385433 |
| videogioco                             | gioco per pc          | 4.0                |
| cura                                   | operazione chirurgica | 2.796967025997495  |
| risaia                                 | patata                | 3.0949584304197235 |
| appunti                                | compito               | 2.9005147462474645 |
| volpe                                  | cellula del sangue    | 0                  |
| cloruro di sodio                       | sale                  | 3.999999999999998  |
| reddito                                | qualità della vita    | 2.6561827261856052 |

**2nd_task_bnsyns_retrieval:**
| word1                                  | word2                 | syn1         | syn2         | lemmas_syn1                                                                          | lemmas_syn2                                                                                                                |
|----------------------------------------|-----------------------|--------------|--------------|--------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| disturbo bipolare                      | problema              | bn:00010593n | bn:00048242n | disturbo_bipolare,depressione_bipolare,psicosi_maniaco-depressiva                    | problema                                                                                                                   |
| acido                                  | base                  | bn:00000902n | bn:00002771n | acidi,acido,acidi_inorganici                                                         | base,alcali,base_(chimica)                                                                                                 |
| zero assoluto                          | vapore                | bn:00000453n | bn:00080637n | -273°,-273,15°c,zero_assoluto                                                        | vapore_d'acqua,vapor_d'acqua,vapore_acqueo                                                                                 |
| rivoluzione verde                      | vernice               | bn:03594063n | bn:00079613n | rivoluzione_verde                                                                    | lacca,vernice,laccatura                                                                                                    |
| sistema operativo                      | deep learning         | bn:00059123n | bn:02601968n | os,sistema_operativo,so                                                              | deep_learning,apprendimento_approfondito,apprendimento_profondo                                                            |
| olimpiadi internazionali di matematica | teoria                | bn:03701756n | bn:00045632n | olimpiadi_internazionali_della_matematica,imo,olimpiadi_internazionali_di_matematica | ipotesi,possibilità,teoria                                                                                                 |
| el niño                                | equatore              | bn:00030030n | bn:00031294n | enso,el_nino,el_niño                                                                 | equatore,equatore_terrestre,circonferenza_equatoriale                                                                      |
| distintivo                             | vetro                 | bn:00062448n | bn:00040605n | distintivo,spilla,spillo                                                             | vetro,cristalleria,cristallerie                                                                                            |
| dimora                                 | scultore              | bn:00042667n | bn:00069924n | dimora,magione_(architettura),magione                                                | scultori,scultore,scultura                                                                                                 |
| atmosfera                              | ozono                 | bn:00002185n | bn:00060040n | atmosfera_terrestre,aria,atmosfera                                                   | ozonizzatore,ozono,generatore_di_ozono                                                                                     |
| scudo                                  | brocchiero            | bn:00013602n | bn:00013602n | scudo,shields,brocchiero                                                             | scudo,shields,brocchiero                                                                                                   |
| moneta                                 | pagamento             | bn:00016448n | bn:00061119n | cash,bancomat,contante                                                               | pagamento,compenso,corresponsione                                                                                          |
| avena                                  | campo                 | bn:00007439n | bn:00034265n | avena,genere_avena,avena_(botanica)                                                  | campagna,campo_(agricoltura),campo                                                                                         |
| monaco                                 | croce                 | bn:00055633n | bn:00127634n | monachismo,monachesimo,regola_monastica                                              | croce                                                                                                                      |
| cannoniera                             | costa                 | bn:00042239n | bn:00071235n | gunvessel,cannoniere,cannoniera                                                      | riva,costa,sponda                                                                                                          |
| roccia                                 | miniera               | bn:00068046n | bn:00055114n | sasso,roccia,pietra                                                                  | miniera                                                                                                                    |
| leggenda                               | morale                | bn:00032591n | bn:00050794n | epopea,leggenda,leggende                                                             | ammaestramento,morale,lezione                                                                                              |
| campione                               | vincitore             | bn:15948556n | bn:03655783n | il_campione,campione,il_campione_(film_1931)                                         | il_vincitore_(film_1996),vincitore,il_vincitore                                                                            |
| dado                                   | cubo                  | bn:00024258n | bn:00024258n | cubo,esaedro_regolare,cuboide                                                        | cubo,esaedro_regolare,cuboide                                                                                              |
| topologia                              | struttura             | bn:00003800n | bn:01049167n | topologia,analisi_situs,studio_dei_luoghi                                            | struttura_matematica,struttura_(matematica)                                                                                |
| cappella                               | cavo                  | bn:15478652n | bn:01583344n | cappella,cappella_(gruppo_musicale),cappella_(progetto_musicale)                     | cavo,cavo_(gruppo_musicale)                                                                                                |
| flusso di cassa                        | fiume                 | bn:00016458n | bn:00067948n | flusso_di_cassa,cash_flow,flussi_di_cassa                                            | corsi_d'acqua,fiume,rivo                                                                                                   |
| serial killer                          | assassino             | bn:00070599n | bn:00032175n | assassina_seriale,serial_killer,serial-killer                                        | assassinio,omicidio,uccisione                                                                                              |
| matrice                                | molecola              | bn:01600840n | bn:00006815n | metaplasma,matrice_extracellulare,spazio_extracellulare                              | brandello,atomo,briciolo                                                                                                   |
| moda                                   | stile                 | bn:00023619n | bn:00032400n | mania_del_momento,moda,moda_breve                                                    | stile_espressivo,stile,stile_artistico                                                                                     |
| vessillologia                          | bandiera              | bn:00646030n | bn:00030968n | vessillologo,vexillologist,vessillologia                                             | bandiera_di_stato,bandiera_nazionale,bandiera_civile                                                                       |
| trattato di maastricht                 | europa                | bn:01352045n | bn:00021127n | accordi_di_maastricht,trattato_sull'unione_europea,trattato_di_maastricht            | unione_europea,cee,comunità_economica_europea                                                                              |
| geyser                                 | sorgente              | bn:00040351n | bn:00036077n | geyser,scaldabagno                                                                   | scaturigine,fonte,polla                                                                                                    |
| saccarosio                             | carboidrato           | bn:00068722n | bn:00015853n | inversione_del_saccarosio,zucchero,saccarosio                                        | glucide,carboidrato,saccaride                                                                                              |
| spiaggia                               | costa                 | bn:00009263n | bn:00071235n | spiaggia,arenile,lido                                                                | riva,costa,sponda                                                                                                          |
| mercato azionario                      | borsa                 | bn:00070218n | bn:00070218n | mercato_azionario,borsa_valori,borsa                                                 | mercato_azionario,borsa_valori,borsa                                                                                       |
| tradizione                             | artigianato           | bn:00024592n | bn:00023499n | tradizionale,tradizione,costumanza                                                   | arte,abilità,abilità_professionale                                                                                         |
| romanzo                                | scrittore             | bn:00058201n | bn:00007287n | romanzi,romanzo,romanziere                                                           | autore_televisivo,scrittore,autore                                                                                         |
| panino                                 | subway                | bn:00069164n | bn:03345051n | sandwich,tramezzino,j.-montagne-conte-di-sandwich                                    | subway,subway_(azienda),subway_(ristorante)                                                                                |
| acustica                               | suono                 | bn:00000989n | bn:00000986n | dati_acustici,acustica,fisica_acustica                                               | onda_acustica,suono,onda_sonora                                                                                            |
| scherma                                | ginnastica            | bn:00034059n | bn:00042326n | scherma,scherma_(sport),combattimento_con_la_spada                                   | attività_ginniche,ginnastica,educazione_fisica                                                                             |
| scrittore                              | regalo                | bn:00007287n | bn:02345076n | autore_televisivo,scrittore,autore                                                   | il_regalo,regalo                                                                                                           |
| bosco                                  | tiger woods           | bn:00035868n | bn:03181223n | bosco_misto,bosco,foresta                                                            | tiger_woods,eldrick_tont_woods                                                                                             |
| nuvola                                 | finestra              | bn:02292735n | bn:00081292n | nuvola_(informatica),nuvola                                                          | finestra,finestra_(informatica),window                                                                                     |
| jpeg                                   | pdf                   | bn:00838809n | bn:01745594n | joint_photographic_experts_group,jpeg,jpg                                            | .pdf,adobe_acrobat_document,portable_document_format                                                                       |
| regista                                | capo                  | bn:00032179n | bn:02347758n | chief_officer,executive,dirigente                                                    | direttore,capo,leader                                                                                                      |
| tassa                                  | brexit                | bn:00034084n | bn:14118606n | infeudazione,feudo,feudi                                                             | referendum_sulla_permanenza_del_regno_unito_nell'unione_europea,fuoriuscita_della_gran_bretagna_dall'unione_europea,brexit |
| impollinazione                         | stame                 | bn:00063375n | bn:00073884n | anemofila,amenofilia,impollinazione                                                  | stame,stami,androceo                                                                                                       |
| videogioco                             | gioco per pc          | bn:00021477n | bn:00021477n | videogame,video_game,videogioco                                                      | videogame,video_game,videogioco                                                                                            |
| cura                                   | operazione chirurgica | bn:00024461n | bn:00059129n | farmaco,rimedio,cura                                                                 | chirurgia,intervento,intervento_chirurgico                                                                                 |
| risaia                                 | patata                | bn:00060141n | bn:00047481n | risaia,campi_di_riso,risaie                                                          | patata_(alimento),solanum_tuberosum,patata                                                                                 |
| appunti                                | compito               | bn:03223016n | bn:00894769n | appunti_(informatica),appunti,clipboard                                              | compito                                                                                                                    |
| cloruro di sodio                       | sale                  | bn:00021159n | bn:00021159n | nacl,cloruro_di_sodio,salgemma                                                       | nacl,cloruro_di_sodio,salgemma                                                                                             |
| reddito                                | qualità della vita    | bn:14505599n | bn:00065542n | reddito                                                                              | qualità_di_vita,qualità_della_vita,qol                                                                                     |

**Overall results:**
```
Task 1: Semantic Similarity
        Evaluation - Person: 0.77, Spearman: 0.79

Task 2: Sense Identification.

        Accuracy: (59%)
```

![Chart](./reports/Evaluation:_Manual_Annotation_vs_Nasari_Embeddings
.png)

## Authors

- Vittorio Paragallo
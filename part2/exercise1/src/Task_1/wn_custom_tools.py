from math import log
from nltk.corpus import wordnet as wn
import itertools
import math
#max(max(len(hyp_path) for hyp_path in ss.hypernym_paths()) for ss in wn.all_synsets())
max_wn_depth = 19

def depth_path(synset, lcs):
    """
    It mesures the distance (depth) between the given Synset and the
    WordNet's root choosing only the path passing through lcs
    :param synset: synset to reach from the root
    :param lcs: Lowest Common Subsumer - the first common sense
    :return: the minimum path which contains LCS
    """

    paths = synset.hypernym_paths()
    # all path containing LCS
    paths = list(filter(lambda x: lcs in x, paths))
    return min(len(path) for path in paths)

def lowest_common_subsumer(synset1, synset2):
    """
    :param synset1: primo synset in cui cercare l'iperonimo comune
    :param synset2: secondo synset in cui cercare l'iperonimo comune
    :return: restituiste il primo degli iperonimi più specifici ai 2 synset (ci possono essere più hyperonimmi comuni alla stessa altezza)
    """

    if synset1 == synset2:
        return synset1
    
    # for both syns we take all the nodes in the upwards path 
    syn1_ancestors_all_paths = set(itertools.chain(*synset1.hypernym_paths()))
    syn2_ancestors_all_paths = set(itertools.chain(*synset2.hypernym_paths()))
    
    # we get a set of common nodes in the syns ancestor paths
    common_ancestors = syn1_ancestors_all_paths & syn2_ancestors_all_paths
    # creates a list of tuples common_ancestor and it's depth and returns the element
    #with max max_depth()
    lowest_common = max(
          [(common_ancestor, common_ancestor.max_depth())
              for common_ancestor in common_ancestors],
                key=lambda i: i[1],
                default=None)
    if (lowest_common is None):
      return None

    return lowest_common[0]

def distance(synset1, synset2):
    """
    :param synset1: first synset
    :param synset2: second synset
    :return: distance between the two synset, it  considers the sitution in whch the nodes are the same synset or are in the same path or are in a different path with a common subsumer
    """

    lcs = lowest_common_subsumer(synset1, synset2)

    if lcs is None:
        return None


    synset1_path_to_root = synset1.hypernym_paths()
    synset2_path_to_root = synset2.hypernym_paths()
    # path from LCS to root
    lcs_to_root_paths = lcs.hypernym_paths()
    lcs_to_root_nodes = set()
    for lcs_to_root_path in lcs_to_root_paths:
        for node in lcs_to_root_path:
            lcs_to_root_nodes.add(node)
    # distinct nodes among all the paths from lcs to root without lcs
    lcs_to_root_nodes.remove(lcs) 

    # remove from synsets paths the part of paths from lcs to nodes
    synset1_partial_path = list(
        map(lambda x: [y for y in x if y not in lcs_to_root_nodes], synset1_path_to_root))
    synset2_partial_path = list(
        map(lambda x: [y for y in x if y not in lcs_to_root_nodes], synset2_path_to_root))

    # filter only the path containing lcs
    synset1_path_to_lcs = list(filter(lambda x: lcs in x, synset1_partial_path))
    synset2_path_to_lcs = list(
        filter(lambda x: lcs in x, synset2_partial_path))
    
    # -2 to remove the source nodes so the distance on same node is 0
    return min(list(map(lambda x: len(x), synset1_path_to_lcs))) + min(list(map(lambda x: len(x), synset2_path_to_lcs))) - 2

def wu_palmer_metric(synset1, synset2):
    """
    Implementations of the Wu-Palmer metric.
    """
    lcs = lowest_common_subsumer(synset1, synset2)
    if lcs is None:
        return 0

    depth_lcs = depth_path(lcs, lcs)
    depth_s1 = depth_path(synset1, lcs)
    depth_s2 = depth_path(synset2, lcs)
    result = (2 * depth_lcs) / (depth_s1 + depth_s2)
    return result * 10

def shortest_path_metric(synset1, synset2):
    """
    Implementations of the Shortest Path metric.
    """
    len_s1_s2 = distance(synset1, synset2)
    if len_s1_s2 is None:
        return 0
    # normalizzare [0-2maxdepth] a [0,1]   
    #return 2 * max_wn_depth - len_s1_s2
    return 1 / (len_s1_s2+1)

def leakcock_chodorow_metric(synset1, synset2):
    """
    Implementations of the Leakcock-Chodorow metric.
    """

    len_s1_s2 = distance(synset1, synset2)
    if len_s1_s2 is None:
        return 0
    return -math.log((len_s1_s2 + 1) / (2.0 * max_wn_depth))



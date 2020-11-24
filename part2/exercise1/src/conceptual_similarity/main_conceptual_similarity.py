import time
import csv
import math
from correlation_indices import pearson_correlation_index, spearman_correlation_index
from wn_custom_tools import wu_palmer_metric, leakcock_chodorow_metric, shortest_path_metric, max_wn_depth
from nltk.corpus import wordnet as wn
    
def conceptual_similarity(inputfilepath, outputfilepath):
  """
  Computes the conceptual similarity and Pearson/Spearman indexes.
  results are written in outputfile.
  :param input and output string filespaths.
  """

  # parse the input file and get a list of triples like (w1,w2,goldannotation)
  reader = csv.reader(open(inputfilepath, 'r'), delimiter=',')
  # skip header
  next(reader, None)
  ws353 = [(line[0],line[1], float(line[2]) ) for line in reader]
  print("- WordSim353.csv parsed.")

  # Looping over the list of all the three metrics.
  similarities_results = []

  for w1, w2, gold in ws353:
      wp_couple_values = []
      sp_couple_values = []
      lc_couple_values = []

      for s1 in wn.synsets(w1):
          for s2 in wn.synsets(w2):
              wp_couple_values.append(wu_palmer_metric(s1, s2))
              # simpath(s1,s2) are between 0 and 2*depthMax
              #so we normalize on 10 to agree with golden
              sp_couple_values.append(shortest_path_metric(s1, s2) * 10 / (2 * max_wn_depth))
              # the values of simLC(s1, s2) are in the interval(0, log(2*depthMax + 1)]
              lc_couple_values.append(leakcock_chodorow_metric(s1, s2) * 10 / math.log(2 * max_wn_depth+1))
      # exclude words without senses
      if (len(wp_couple_values) != 0) and (len(sp_couple_values) != 0) and (len(lc_couple_values) != 0):
          similarities_results.append(
              {"w1": w1,"w2": w2,
                "wp": max(wp_couple_values), "sp": max(sp_couple_values), "lc": max(lc_couple_values),
                "gold": gold})

  # the list of golden annotations
  golden = [item['gold'] for item in similarities_results]
  
  wp_pearson_index = pearson_correlation_index(
      golden, [item['wp'] for item in similarities_results])
  wp_spearman_index = spearman_correlation_index(
      golden, [item['wp'] for item in similarities_results])

  sp_pearson_index = pearson_correlation_index(
      golden, [item['sp'] for item in similarities_results])
  sp_spearman_index = spearman_correlation_index(
      golden, [item['sp'] for item in similarities_results])

  lc_pearson_index = pearson_correlation_index(
      golden, [item['lc'] for item in similarities_results])
  lc_spearman_index = spearman_correlation_index(
      golden, [item['lc'] for item in similarities_results])

  with open(outputfilepath, "w") as out:
      out.write("metric, Pearson, Spearman\n")
      out.write("wp, {}, {}\n".format(wp_pearson_index, wp_spearman_index))
      out.write("sp, {}, {}\n".format(sp_pearson_index, sp_spearman_index))
      out.write("lc, {}, {}\n".format(lc_pearson_index, lc_spearman_index))
      out.write("____________________________________\n")
      out.write("W1, W2, WP, SP, LC, GOLD\n")
      out.write("\n".join(
          ["{}, {}, {:.2f}, {:.2f}, {:.2f}, {}".format(
              result['w1'],
              result['w2'],
              result['wp'],
              result['sp'],
              result['lc'],
              result['gold']
          ) for result in similarities_results]))
      out.close()


if __name__ == "__main__":
  conceptual_similarity(
      './part2/exercise1/input/WordSim353.csv',
      './part2/exercise1/output/task1_results.csv')

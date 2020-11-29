import time
import csv
import math
from correlation_indices import pearson_correlation_index, spearman_correlation_index
from wn_custom_tools import wu_palmer_metric, leakcock_chodorow_metric, shortest_path_metric, max_wn_depth
from nltk.corpus import wordnet as wn
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def plot_correlation_index(gold_measure, computed_measure, title, pearson_value, spearman_value):
  df = pd.DataFrame()
  df['gold measure'] = gold_measure
  df['computed measure'] = computed_measure
  #fit_reg=True estimate and plot a regression model relating the x and y variables.
  sns.lmplot('gold measure', 'computed measure', data=df, fit_reg=True)
  plt.title(title)
  title = title.replace(' ', '_')
  plt.text(9, -2, f'Pearson: {pearson_value}\nSpearman: {spearman_value}', bbox=dict(fill=False, edgecolor='green', linewidth=2))
  plt.savefig(f'./part2/exercise1/reports/{title}.png', bbox_inches='tight')




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

  similarities_results = []

  for w1, w2, gold in ws353:
      # stores wu palmier results
      wp_couple_values = []
      # stores shortest path results
      sp_couple_values = []
      # stores  leakcock chodorow results
      lc_couple_values = []
      
      # for each combination of senses the 3 metrics are computed
      for s1 in wn.synsets(w1):
          for s2 in wn.synsets(w2):
              wp_couple_values.append(wu_palmer_metric(s1, s2))
              # normalize on 10 to agree with golden
              sp_couple_values.append(shortest_path_metric(s1, s2) * 10)
               # the values of simLC(s1, s2) are in the interval(0, log(2*depthMax + 1)] so are normalized on 10 
              #to agree with golden
              lc_couple_values.append(leakcock_chodorow_metric(s1, s2) * 10 / math.log(2 * max_wn_depth + 1))
                 
      # store the results saving only the maximum similarity value for each metric
      # it is performed only if both wn.synsets(w1) and wn.synsets(w2) returrned synset 
      # and so all the metrics were computed. We check just the first metric list lenght
      if len(wp_couple_values)>0:
        similarities_results.append(
                {"w1": w1,"w2": w2,
                  "wp": max(wp_couple_values), "sp": max(sp_couple_values), "lc": max(lc_couple_values),
                  "gold": gold})

  # the list of golden annotations
  golden = [item['gold'] for item in similarities_results]
  #compute pearson and spearman on wu palmier metric
  wp_sim_values = [item['wp'] for item in similarities_results]
  wp_pearson_index = pearson_correlation_index(golden, wp_sim_values)
  wp_spearman_index = spearman_correlation_index(golden, wp_sim_values)
  plot_correlation_index(golden, wp_sim_values, 'Wu & Palmier',
                         f'{wp_pearson_index:.{2}}',f'{wp_spearman_index:.{2}}')

  #compute pearson and spearman on shortest path metric
  sp_sim_values = [item['sp'] for item in similarities_results]
  sp_pearson_index = pearson_correlation_index(golden, sp_sim_values)
  sp_spearman_index = spearman_correlation_index(golden, sp_sim_values)
  plot_correlation_index(golden, sp_sim_values, 'Shortest Path',
                         f'{sp_pearson_index:.{2}}',f'{sp_spearman_index:.{2}}')

  #compute pearson and spearman on  leakcock chodorow metric
  lc_sim_values = [item['lc'] for item in similarities_results]
  lc_pearson_index = pearson_correlation_index(golden, lc_sim_values)
  lc_spearman_index = spearman_correlation_index(golden, lc_sim_values)
  plot_correlation_index(golden, lc_sim_values, 'Leakcock Chodorow',
                         f'{lc_pearson_index:.{2}}',f'{lc_spearman_index:.{2}}')

  # save results
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

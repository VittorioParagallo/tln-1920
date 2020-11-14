import math
import numpy as np
import nltk
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from nltk.tokenize import sent_tokenize

from utilities import sentences_cosine_similarity, create_vectors, weighted_overlap


def parse_nasari_dictionary():
    """
    It parse the Nasari input file, and it converts into a more convenient
    Python dictionary.

    :return: a dictionary representing the Nasari input file. Format: {word: {term:weight}}
    """

    nasari_dict = {}
    with open(config["nasari"], 'r', encoding="utf8") as file:
        for line in file:
            splits = line.split("\t")
            vector_dict = {}

            for term in splits[2:config["limit"]]:
                k = term.split("_")
                if len(k) > 1:
                    vector_dict[k[0]] = k[1]

            nasari_dict[splits[1].lower()] = vector_dict

    return nasari_dict


def tokenize_text(text):
    """
    It divides the text in groups. Each group..

    :param text: input text
    :return: list of sequences (list of all groups of word)
    """

    sequences = []
    text = text.lower()
    sent_tokens = sent_tokenize(text)
    sentences = []
    j = 0

    for sent_token in sent_tokens:
        sequences.append(nltk.word_tokenize(sent_token))
        sentences.append(sent_token)

    print("\tFound {} sequences".format(str(len(sequences))))
    return sequences, sentences


def clustering(similarities, sentences):
    """
    It uses K-Means clustering algorithm in order to compute and move if
    necessary the breakpoint of the input text.

    :param similarities:  list of similarity score for every sentence in the text.
    Each element is the sum of the two similarity of a sentence with the previous
    and the next sentence.
    :param sentences: a list of string containing the sentences of the input text
    :return: a list containing one or more list of breakpoint positions (one
    list for each iteration)
    """
    print("\tComputing clusters using K-Means...")
    sentences_similarities = np.array(similarities)
    #trasponi da riga a colonna
    data = sentences_similarities.reshape(-1, 1)  # needed for cluster computin

    # Sets the best cluster size within the minimum and maximum supplied. Eg.: 2,10
    clusters_size_ranges = np.arange(2, 20)
    clusters_sizes = {}
    #verifica qual è il numero migliore di cluster nel range fornito
    for size in clusters_size_ranges:
        model = KMeans(n_clusters=size).fit(data)
        predictions = model.predict(data)
        clusters_sizes[size] = silhouette_score(data, predictions)
    best_clusters_size = max(clusters_sizes, key=clusters_sizes.get)
    print("\t\tThe best cluster group size is: {}".format(best_clusters_size))

    # Compute Kmeans with best cluster size
    kmeans = KMeans(n_clusters=best_clusters_size)
    kmeans.fit(data)
    matix_clusterized = kmeans.labels_

    # Calculating beginning windows lenght based on sentences evenly splitted in contiguos clusters
    initial_window_size = len(matix_clusterized) / best_clusters_size
    print("\t\tThe initial window size is: {:.3f}".format(initial_window_size))

    # Windows is the part of the array that contains cluster's id for each sentence
    # (original: "contiene l'id dei cluster per frasi")
    windows_list = np.array_split(sentences, best_clusters_size)
    # print("Tmp sliced array: {}".format(windows_list)) # DEBUG

    final_list = [l.tolist() for l in windows_list]

    iterations_log = []
    stable = False  # if true -> convergence
    offset = 1
    end = False
    while not end:
        stable = True
        end = True
        for i in range(len(final_list)):
            if i > 0:
                if offset < len(final_list[i - 1]):
                  end = end and False
                  last_prev_vs_prev_similarity = sentences_cosine_similarity(
                      ' '.join(final_list[i - 1][:-offset]
                               ),  ' '.join(final_list[i - 1][-offset:]))
                  last_prev_vs_curr_similarity = sentences_cosine_similarity(
                      ' '.join(final_list[i - 1][-offset:]),
                      ' '.join(final_list[i]))
                else:
                  last_prev_vs_prev_similarity = 1
                  last_prev_vs_curr_similarity = 0

                if last_prev_vs_curr_similarity > last_prev_vs_prev_similarity:
                    stable = False
                    elem_to_move = final_list[i - 1][-offset:]
                    del final_list[i - 1][-offset:]
                    final_list[i][0:0] = elem_to_move
                else:
                    if offset < len(final_list[i]):
                      end = end and False
                      first_curr_vs_curr_similarity = sentences_cosine_similarity(
                          ' '.join(final_list[i][offset:]), ' '.join(final_list[i][:offset]))
                      first_curr_vs_prev_similarity = sentences_cosine_similarity(
                          ' '.join(final_list[i][:offset]), ' '.join(final_list[i - 1]))
                      if first_curr_vs_prev_similarity > first_curr_vs_curr_similarity:
                          stable = False
                          elem_to_move = final_list[i][:offset]
                          del final_list[i][:offset]
                          final_list[i - 1].extend(elem_to_move)

        # Just for logging
        iteration_log_line = []
        for j in range(len(final_list)):
            if j == 0:
                iteration_log_line.append(len(final_list[j]))
            else:
                iteration_log_line.append(
                    (len(final_list[j]) + iteration_log_line[j - 1]))
        iterations_log.append(iteration_log_line)
        print('------------------------------------------------------')
        print('\n'.join(' '.join(map(str, sl)) for sl in iterations_log))
        if stable:
          offset += 1

    print("\tDone.")
    segmented_result = '\n\n\n\t<NEW TILE>\n\n\n'.join(
        '\n'.join(map(str, sl)) for sl in final_list)
    text_file = open("./part3/exercise4/output/" +
                     config["input"].split('/')[-1].split('.')[0] + "_segmented.csv", "w")
    text_file.write(segmented_result)
    text_file.close()
    return iterations_log


def segmentation():
    print('Starting segmentation.')

    print('\tLoading Nasari...')
    # input
    nasari = parse_nasari_dictionary()
    with open(config["input"]) as file:
        lines = file.readlines()
    text = ''.join(lines)
    print('\tDone.')

    # Text tokenization
    print('\tBegin tokenization...')
    #divides the text in sentences with nltk sent_tokenize
    #and return both list of sentences and tokenized sentences
    #ex.
    #sequences[0]=['in', 'one', 'account', 'it', .....
    #sentences[0]= "in one account it is argued that .....
    sequences, sentences = tokenize_text(text)
    print('\tDone.')

    # Compute similarity between neighbors
    print('\tComputing similarity...')
    similarities = list(np.zeros(len(sequences)))
    for i in range(1, len(sequences) - 1):
        prev = create_vectors(sequences[i - 1], nasari)
        current = create_vectors(sequences[i], nasari)
        next_ = create_vectors(sequences[i + 1], nasari)

        # Because the Weighted Overlap measures the similarity between two
        # vectors representing two sentences (couple term:weight), we need to
        # compute the Square Root Weighted Overlap, which produces as output
        # the similarity between the two sentences represented in vector notation.

        # Computing Square Root Weighted Overlap between prev and current
        # sentences
        similarity = []
        for x in prev:
            for w in current:
                similarity.append(math.sqrt(weighted_overlap(x, w)))
        left = max(similarity) if len(similarity) > 0 else 0

        # Computing Square Root Weighted Overlap between next and current
        # paragraphs
        similarity = []
        for x in next_:
            for w in current:
                similarity.append(math.sqrt(weighted_overlap(x, w)))
        right = max(similarity) if len(similarity) > 0 else 0

        # Final similarity
        similarities[i] = (left + right) / 2
    print("\tDone.")

    del nasari

    breakpoints = clustering(similarities, sentences)

    # Plotting -----------------------------------------------------------------
    print("\tPlotting...")

    length = len(similarities)
    x = np.arange(0, length, 1)
    y = np.array(similarities)

    fig, ax = plt.subplots()
    ax.plot(x, y, label='blocks cohesion', color='c')

    # Plotting the last computed list of breakpoint
    for x in breakpoints[-1]:
        ax.axvline(x, color='r', linewidth=1)

    ax.set(xlabel='sentences', ylabel='similarity',
           title='Block similarity')
    ax.grid()
    ax.legend(loc='best')

    # Saving the plot in output folder
    now = datetime.now().strftime("Plot - %d.%m.%Y-%H:%M:%S")  # dd/mm/YY H:M:S
    plt.savefig('{}{}.png'.format(config["output"], now))
    plt.show()
    print("\tPlot saved in output folder.")

    breakpoints_results = '\n'.join(
        '\t'.join(map(str, sl)) for sl in breakpoints)
    text_file = open("./part3/exercise4/output/" +
                     config["input"].split('/')[-1].split('.')[0] + "_tiling_process.csv", "w")
    text_file.write(breakpoints_results)
    text_file.close()

    print('Segmentation ended.')


global config  # Dictionary of the configuration. Used across all the script.

if __name__ == "__main__":
    config = {
        "input": "part3/exercise4/input/origin_of_lindyhop.txt",
        "output": "part3/exercise4/output/",
        "nasari": "part3/exercise4/resources/NASARI_lexical_english.txt",
        "limit": 14  # first x elem of nasari vector
    }

    segmentation()

# Summarization with NASARI

Given a set of text documents create summaries with 10%, 20% and 30% reduction

### Input
The input is a set of text file in folder 'text_document':
- Andy-Warhol.txt
- Ebola-virus-disease.txt
- Life-indoors.txt
- Napoleon-wiki.txt
and a lemma vector resource file:
- dd-small-nasari-15.txt

### Output
The script outputs in a in the output folder 12 files. More specifically 3 files for each document with 10, 20 and 30% reduction: 

- 10-Andy-Warhol.txt
- 10-Ebola-virus-disease.txt
- 10-Life-indoors.txt
- 10-Napoleon-wiki.txt
-  20-Andy-Warhol.txt
- 20-Ebola-virus-disease.txt
- 20-Life-indoors.txt
- 20-Napoleon-wiki.txt
-  30-Andy-Warhol.txt
- 30-Ebola-virus-disease.txt
- 30-Life-indoors.txt
- 30-Napoleon-wiki

## Structure
The scrips is exercise3.py archived in the src and includes:
- main in which all the calls are done
- parse_document to retrieve the text input file as a set of data
- parse_nasari_dictionary parses the nasary text file in a dictionary
- create_context which, given in input a text and the nasari dictionary, preprocess the text and transforms it in a nasari representation
- weighted_overlap to score similarity considering elements rank in nasari vectors
- summatization creates the summarized version of the input file based on topic similarity



## Authors

- Vittorio Paragallo
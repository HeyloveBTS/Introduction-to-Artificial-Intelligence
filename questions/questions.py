from encodings import utf_8
import imp
import string as str
import nltk
import sys
import os
import math
from nltk.corpus import stopwords

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    corpus = dict()

    # Go through all of the.txt files in the specified directory:
    for filenames in os.listdir(directory):
        filePath = os.path.join(directory, filenames)
        if filenames.endswith(".txt") and os.path.isfile(filePath):
            # Encoding UTF-8 https://blog.hubspot.com/website/what-is-utf-8
            with open(filePath, "r", encoding= 'utf_8') as file:
                corpus[filenames] = file.read() # Read file into string

    return corpus



def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    
    # Extract the lowercased tokens
    tokens = nltk.word_tokenize(document.lower())
    stops = nltk.corpus.stopwords.words('english') # nltk stop words https://pythonspot.com/nltk-stop-words/
    wordFiltered = []

    # Make sure all tokens are lowercase, without punctuation or stopwords.
    for token in tokens:
        if token not in stops and token not in str.punctuation:
            wordFiltered.append(token)
    
    return wordFiltered
 


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # Create a dictionary to determine how many documents each word appears in:
    wordCount = dict()

    # Iterate through documents
    for document in documents:
        docWords = set(documents[document])
        # looking at unique words in each document
        for word in docWords:
            if word in wordCount:
                wordCount[word] += 1
            else:
                wordCount[word] = 1

    # Calculate idfs for each word:
    IDFs = dict()
    for word in wordCount:
        IDFs[word] = math.log((len(documents) / wordCount[word]))

    return wordCount



def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    fileValue = {file:0 for file in files}

    # Iterate over the query, limiting it to words found in the idf dictionary.

    for word in query:
        if word in idfs:
            # Iterate across the corpus
            for file in files:
                fileValue[file] += files[file].count(word) * idfs[word]

    # Files ranked according to the sum of tf-idf values 
    filesRank = sorted(fileValue.items(), key=lambda x: x[1], reverse=True)
    topFiles = [i[0] for i in filesRank][:n]

    return topFiles
    

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # Initiate tfidf-dict
    TFIDF_dict = dict()

    # Iterate through sentences:
    for sentence in sentences:
        senLength = len(sentences[sentence])
        TFIDF_dict[sentence] = {sentence:{}}
        TFIDF_dict[sentence]["idf"] = 0
        TFIDF_dict[sentence]["length"] = 0
        TFIDF_dict[sentence]["q_density"] = 0

        # Iterate through query words:
        for word in query:
            # Update the query word's score if it appears in the sentence word list.
            if word in sentences[sentence]:
                TFIDF_dict[sentence]["idf"] += idfs[word]
                TFIDF_dict[sentence]["q_density"] += sentences[sentence].count(word)/ senLength

    # Rank sentences by idf and density
    sortedSent = sorted([sentence for sentence in sentences], key= lambda x: (TFIDF_dict[x]['idf'], TFIDF_dict[x]['q_density']), reverse=True)

    return sortedSent[:n]
 



if __name__ == "__main__":
    main()

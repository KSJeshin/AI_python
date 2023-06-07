import nltk
import sys
import string
import math
import os

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
    #raise NotImplementedError
    files = os.listdir(directory)
    files_dict = {}
    for file in files:
        with open(os.path.join(directory, file)) as f:
            files_dict[file] = f.read() 
      
    return (files_dict)

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    #raise NotImplementedError
    n_tokens = []
    #print(sentence)
    #tokens = nltk.tokenize.word_tokenize(document)
    #tokens = nltk.regexp_tokenize(document, pattern='\w+|\$[\d\.]+|\S+|\'+', gaps=True)
    tokens = nltk.regexp_tokenize(document, pattern='\s+', gaps=True)
    count = 0
    for token in tokens:
        token = token.lower()
        if token.islower() and token not in nltk.corpus.stopwords.words("english"):
            if any(c_item in token for c_item in string.punctuation):
                sub_string = token.translate(token.maketrans(string.punctuation, ' '*len(string.punctuation)))
                n_tokens += [sub_token for sub_token in nltk.tokenize.word_tokenize(sub_string) if not sub_token in nltk.corpus.stopwords.words("english")]
            else:
                n_tokens.append(token)
            '''
            if count<20:
                print(n_token)
            count+=1
            '''
    return n_tokens

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    #raise NotImplementedError
    total_docs = len(documents)
    #print(f'Total docs:{total_docs}')
    idf_map = {}
    for part in documents:
        for word in documents[part]:
            if word in idf_map.keys():
                continue
            idf_map[word] = 0
            for part in documents:
                if word in documents[part]:
                    idf_map[word] += 1
            idf_map[word] = math.log(total_docs/idf_map[word])
    
    return idf_map

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    #raise NotImplementedError
    ranked_files = []
    for filename in files:
        file_rank = 0
        for q_token in query:
            file_rank += (files[filename].count(q_token)/len(files[filename])) * (idfs[q_token] if idfs[q_token] else 0)
            
        for count in range(len(ranked_files)):
            if file_rank>=ranked_files[count][1]:
                ranked_files.insert(count, (filename, file_rank))
                break
        if not ranked_files or count == len(ranked_files)-1:
            ranked_files.append((filename, file_rank))        
    
    return [ranked_files[count][0] for count in range(n)]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    #raise NotImplementedError
    ranked_sentences = []
    for sentence in sentences:
        sentence_rank = 0
        #print(f'sentence:{sentence}')
        #print(f'query_tokens:{query}')
        for q_token in query:
            #print(f'query_token:{q_token}, idf_value: {idfs[q_token]}')
            if q_token in sentences[sentence]:
                sentence_rank += idfs[q_token] if idfs[q_token] else 0
        #print(f'query_tokens:{query}, total_idf:{sentence_rank}') 
        for count in range(len(ranked_sentences)):
            if sentence_rank>=ranked_sentences[count][1]:
                ranked_sentences.insert(count, (sentence, sentence_rank))
                break
        if not ranked_sentences or count == len(ranked_sentences)-1:
            ranked_sentences.append((sentence, sentence_rank))
            
    # Adjusting the ranking based on query density
    final_ranking = []
    count = 0
    while(True):
        sub_count = 0
        while(count + sub_count <= len(ranked_sentences)-2 and ranked_sentences[count][1] ==
              ranked_sentences[count+sub_count+1][1]):
            sub_count += 1
        final_ranking += rerank_sent(query, ranked_sentences[count:count+sub_count+1], sentences)
        #print(f'Sentence count:{count}, sub_count: {sub_count}')
        count += sub_count+1
        if len(final_ranking)>=n or count >= len(ranked_sentences):
            break
  
    return [final_ranking[count] for count in range(n)]

def rerank_sent(query, sent_chunk, sentences):
    reranked_chunk = []
    for sentence in sent_chunk:
        q_density = 0
        for q_token in query:
            q_density += 1 if q_token in sentences[sentence[0]] else 0
        q_density /= len(sentences[sentence[0]])
        
        for count in range(len(reranked_chunk)):
            if q_density>=reranked_chunk[count][1]:
                reranked_chunk.insert(count, (sentence[0], q_density))
                break
        if not reranked_chunk or count == len(reranked_chunk)-1:
            reranked_chunk.append((sentence[0], q_density))
    
    return [reranked_sent[0] for reranked_sent in reranked_chunk]
    

if __name__ == "__main__":
    main()

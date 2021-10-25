from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import nltk
import random

stemmer = LancasterStemmer()

def get_intent_data(file, ignore_words=['?']):
    '''Gets data from intents file.

    Args:
        file: Intents file data.
        ignore_words: Words to ignore.

    Returns:
        words, intents and intent_pairs.
    '''
    words = set() # All words and vocubulary
    intents = set() # Intents
    intent_pairs = list() # Combination of patterns and intents

    # Populate lists with intent data
    for intent in file['intents']:
        for pattern in intent['patterns']:
            # Tokenizing each word in a sentance
            word_tokens = set(nltk.word_tokenize(pattern))
            # Add tokens to words set
            words.update(word_tokens)
            # Ascoiate intent and word_tokens
            intent_pairs.append((word_tokens, intent['tag']))
            # Add current intent tag to intents set
            intents.add(intent['tag'])

    # Stem and lower each word and remove duplicates
    words = set([stemmer.stem(w.lower()) for w in words if w not in ignore_words])
    words = sorted(list(words))

    # Create sorted list of intents
    intents = sorted(list(intents))

    return words, intents, intent_pairs

def clean_pattern(pattern, tokenise=True):
    '''Cleans patterns/sentances.

    Args:
        pattern: String containing a setance.

    Returns:
        A list containing a tokanized and stemmed version of sentance.
    '''
    # Checks if tokanise flag is set
    if tokenise:
        # Generates tokens from a sentence
        pattern = nltk.word_tokenize(pattern)
    # Creates a stemmed set of the token words from the input pattern
    pattern_words = set([stemmer.stem(word.lower()) for word in pattern])
    return pattern_words

def build_bag(pattern, words, tokenise=True):
    '''Builds a bag of words

    Args:
        pattern: String containing a sentance.
        words: All words in vocabulary.

    Returns:
        Bag of words.
    '''
    pattern_words = clean_pattern(pattern, tokenise)
    bag = [0]*len(words)
    for i,word in enumerate(words):
        if word in pattern_words:
            bag[i] = 1

    return np.array(bag)

def build_training_bag(words, intents, intent_pairs):
    '''Builds word bags and returns training data.

    Args:
        words: All words and vocubulary.
        intents: Intents.
        intent_pairs: Combination of patterns and intents.

    Returns:
        Training dataset.
    '''
    word_bags = list()
    labels_list = list()
    for pair in intent_pairs:
        labels = [0]*len(intents)
        bag = build_bag(pair[0], words, tokenise=False)
        labels[intents.index(pair[1])] = 1
        word_bags.append(bag)
        labels_list.append(labels)

    return np.array(word_bags), np.array(labels_list)

def return_response(file, intent):
    '''Returns a random valid response from the intents file according to intent.

    Args:
        file: The intents.json file.
        intent: The current intent.

    Returns:
        A valid response sentence according to intent.
    '''
    responses = []
    for tag in file['intents']:
        if tag['tag'] == intent:
            responses = tag['responses']

    return responses[random.randrange(0, len(responses))]
import pickle

file = open('filtered_words.txt', 'r', encoding = 'utf-8')
words = set(file.read().split('\n'))
file.close()

with open('dictionary.p', 'wb') as dictionaryFile:
    pickle.dump(words, dictionaryFile)

#DictionaryFile works as an easily mutatable set of words; can be modified by
#the user faster than a text file
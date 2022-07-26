
def allCharactersEqual(S):
    '''Checks if all characters are equal in an at least 1 length string S'''

    char = S[0].lower()
    for c in S[1:]:
        if (c.lower() != char):
            return False

    return True

with open('words.txt', 'r', encoding = 'utf-8') as wordFile:
    with open('filtered_words.txt', 'w', encoding = 'utf-8') as wordFileFiltered:

        filteredWords = list(filter(lambda line: len(line) > 1 and len(line) < 12 and not allCharactersEqual(line), wordFile.read().split('\n')))
        wordFileFiltered.writelines([filteredWords[0]] + list(map(lambda line: '\n' + line, filteredWords[1:])))
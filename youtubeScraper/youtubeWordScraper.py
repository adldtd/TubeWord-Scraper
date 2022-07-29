import requests
import platform
import random
import os
import pickle
import atexit
import time
import re



class youtubeSearcher():

    def __init__(self):
        self.searchedSet = set() #Records used terms
        self.wordLinks = {} #Records youtube links with dictionary words in them
        self.usedLinks = set() #Records all found links with the search term
        self.words = set() #Records every word in the dictionary

        self.searchTermRepetitions = 0 #Records how many tries it took to get a new search term
        self.additions = 0 #Records how many total appends were made to every word set
        self.failedSearches = 0 #Records how many searches netted zero results
        self.newWords = set() #Records how many new words have been added
        self.sync = True #Shows if the program has finished adding links to both usedLinks and wordLinks; Experimental, only useful for emergencySave

        self.TIMEOUT = 1 #Seconds to wait before making another request
        self.PREDICTED_AVERAGE_ITERATION = self.TIMEOUT + 0.8661545411745707 #Approx. predicted time for each iteration
        self.MAX_LINKS_PER_WORD = 300 #How many links are limited to each word entry in wordLinks
        self.NON_ALPHABETICAL_LINK_CHARS = re.compile(r'[\-\d_]+') #The non alphabetic characters possible in a youtube link; used for splitting a link

        self._load()



    def _genTerm(self):
        '''Helper function for _randomSearchTerm'''

        searchTerm = ''

        length = random.randint(3, 8)
        reps = random.randint(1, 2) #If more than one, the generator will create a multi-"word" search term

        for r in range(reps):
            for i in range(length):
                char = random.randint(97, 122)
                searchTerm += chr(char)
            searchTerm += '+'
        searchTerm = searchTerm[:-1]

        return searchTerm



    def _randomSearchTerm(self):
        '''Returns a search term string made up of random lowercase letters'''
        
        while True:
            searchTerm = self._genTerm()
            if (searchTerm not in self.searchedSet):
                break
            self.searchTermRepetitions += 1

        self.searchedSet.add(searchTerm)
        return searchTerm



    def calcTime(self, seconds):
        '''Given an amount of int or float seconds, returns a string representing a more detailed amount of time'''

        timeStr = ''

        if (seconds > 31536000): #Years
            timeStr += f'{int(seconds // 31536000)}y '
            seconds = seconds % 31536000
        if (seconds > 86400): #Days
            timeStr += f'{int(seconds // 86400)}d '
            seconds = seconds % 86400
        if (seconds > 3600): #Hours
            timeStr += f'{int(seconds // 3600)}h '
            seconds = seconds % 3600
        if (seconds > 60): #Minutes
            timeStr += f'{int(seconds // 60)}m '
            seconds = seconds % 60
        timeStr += f'{round(seconds, 3)}s' #Rounds to three places for convenience

        return timeStr


    #******************************************** CURRENTLY UNUSED
    #def _setInString(self, ST, S):
    #    '''Given a set of non-empty strings ST, returns the set of strings contained in ST that can also be found contained in string S'''
    #
    #    returnSet = set()
    #
    #    for word in ST:
    #        if (word in S):
    #            returnSet.add(word)
    #
    #    return returnSet



    def wordsInString(self, link):
        '''Returns a set containing the valid words inside of string link'''

        returnSet = set()
        linkSequences = self.NON_ALPHABETICAL_LINK_CHARS.split(link)

        for sequence in linkSequences:
            for size in range(1, len(sequence)): #What additional slice of the sequence to check
                for i in range(len(sequence) - size):
                    word = sequence[i:(i + 1) + size]
                    if (word in self.words): #If the word is proper
                        returnSet.add(word)

        return returnSet



    def _placeVideos(self, ST, S):
        '''Given a set of non-empty strings ST, inserts the link S into dictionary wordLinks based on elements of ST as the key'''

        if (len(ST) == 0): #No keys to place S into
            return

        for word in ST:
            if (word in self.wordLinks):
                if (S not in self.wordLinks[word]):
                    if (len(self.wordLinks[word]) < self.MAX_LINKS_PER_WORD):
                        self.wordLinks[word].add(S)
                        self.additions += 1
            else:
                self.wordLinks[word] = set() #Each key points to a set of links
                self.wordLinks[word].add(S)
                self.additions += 1
                self.newWords.add(word)



    def _load(self):
        '''Loads all the data the program has gathered previously in pickle files; should only really be called in the constructor'''

        print('Initializing searchedSet... ', end = '')
        if (os.path.exists("searchedSet.p")):
            with open('searchedSet.p', 'rb') as searchedSetFile:
                self.searchedSet = pickle.load(searchedSetFile)
        print(len(self.searchedSet))

        print('Initializing wordLinks... ', end = '')
        if (os.path.exists("wordLinks.p")):
            with open('wordLinks.p', 'rb') as wordLinksFile:
                self.wordLinks = pickle.load(wordLinksFile)
        print(len(self.wordLinks))

        print('Initializing usedLinks... ', end = '')
        if (os.path.exists("usedLinks.p")):
            with open('usedLinks.p', 'rb') as usedLinksFile:
                self.usedLinks = pickle.load(usedLinksFile)
        print(len(self.usedLinks))

        print('Initializing dictionary... ', end = '')
        if (os.path.exists("dictionary.p")):
            with open('dictionary.p', 'rb') as dictionaryFile:
                self.words = pickle.load(dictionaryFile)
        print(len(self.words))



    def _save(self):
        '''Saves all the data the program has collected to pickle files'''

        with open('searchedSet.p', 'wb') as searchedSetFile:
            pickle.dump(self.searchedSet, searchedSetFile)

        with open('wordLinks.p', 'wb') as wordLinksFile:
            pickle.dump(self.wordLinks, wordLinksFile)

        with open('usedLinks.p', 'wb') as usedLinksFile:
            pickle.dump(self.usedLinks, usedLinksFile)



    def scrapeLinks(self, reps = 1):
        '''Using random search terms, get various youtube links by searching an amount of int reps times. The central function of the
        class'''
        
        method = 0 #What searching "method" the function uses - 1 is for the google api, 0 is for the requests html one

        APIConnect = None
        #if (method == 1):
            #APIConnect = youtubeConnect.youtubeConnect() #Requires authorization

        counter = 0
        start = time.time() #Timer for tracking the time the function takes
        SYS = platform.system()

        with requests.Session() as session:

            while (counter < reps):

                if (SYS == "Windows"):
                    os.system('cls') #EXTRA FUNCTION: Clears the screen
                elif (SYS == "Linux" or SYS == "Darwin"): #Linux and MacOS
                    os.system('clear')
                print(f'Iteration: {counter + 1}/{reps}')

                localUsedLinks = set() #Playlists showing up in results means that the same video link is often repeated; this keeps track of every video went through before all the links are added to the global list
                term = self._randomSearchTerm()
                link = 'https://www.youtube.com/results?search_query=' + term
                print(link)

                if (method == 0): #HTTP request to site

                    time.sleep(self.TIMEOUT)
                    site = session.get(link)

                    linkGet = False

                    for line in site.text.split('\"url\"'): #Useful value to split by ################### NOTE: SOMETIMES GETS DUPLICATE LINKS
                        if ('\"WEB_PAGE_TYPE_WATCH\"' in line and '\"videoId\"' in line): #Means the area is that of a video and not a playlist
                            videoId = line.split('\"videoId\":\"', 1)[1].split('\"', 1)[0] #Is supposed to find a video link value
                            localUsedLinks.add(videoId) #Because this is a set, any duplicates will be removed
                            linkGet = True

                    if (not linkGet): self.failedSearches += 1
                
                elif (method == 1): #Google API; limited by quota
                    
                    response = APIConnect.search(term)
                    
                    if (not type(response) == set): #Means there was an error
                        print("\n" + str(response.status_code) + " " + response.reason)
                        print(response.text)
                        print("\nSwitching to alternate method.")
                        method = 0
                        continue
                        

                    localUsedLinks = response

                    if (len(localUsedLinks) == 0):
                        self.failedSearches += 1


                
                numVids = len(localUsedLinks)
                print(f"{numVids} links found.")

                self.sync = False
                for videoId in localUsedLinks:
                    wordsInId = self.wordsInString(videoId.lower()) #For every videoId, get a set of words inside of it
                    self._placeVideos(wordsInId, videoId)

                self.usedLinks = self.usedLinks.union(localUsedLinks)
                self.sync = True

                counter += 1

        self._save()

        end = time.time() - start

        print('Completed')
        print(f'Search repeats: {self.searchTermRepetitions}')
        print(f'Failed searches: {self.failedSearches}')
        print(f'Total new links added: {self.additions}')

        print('Time taken: ' + self.calcTime(end))
        print(f'Average of {end/reps}s per iteration (Difference: {(end/reps) - self.PREDICTED_AVERAGE_ITERATION})')

        if (len(self.newWords) > 0):
            print('New words:')
            for word in self.newWords:
                print('\t' + word)
        else:
            print('No new words')

        self.searchTermRepetitions = 0
        self.additions = 0
        self.failedSearches = 0
        self.newWords.clear()



    def testValidity(self, links):
        '''Tests if the videoIds in a given list links are all valid by printing response codes'''

        print(str(len(links)) + ' links')
        with requests.Session() as session:
            for videoId in links:

                page = session.get('https://www.youtube.com/watch?v=' + videoId)
                pageText = page.text

                if ('yt-player-error-message-renderer' in pageText): #Assumes only inaccessible videos have this in the HTTP text
                    print(videoId + ': Unavailable\n\t' + page.status_code + ' ' + page.reason)
                else:
                    print(videoId + ': Success')



    def showWordLinks(self, minWordSize = 1, maxWordSize = 11):
        '''Pretty prints the words in wordLinks whose lengths are greater than or equal to int minWordSize'''

        for key in self.wordLinks:
            if (len(key) >= minWordSize and len(key) <= maxWordSize):
                print(f'{key}:')
            
                for link in self.wordLinks[key]:
                    print(f'\t{link}')



    def showLinks(self, word):
        '''Shows the links associated with a given string word, if it exists in the dictionary'''

        if (word in self.wordLinks):
            print(f'{word}:')

            for link in self.wordLinks[word]:
                print(f'\t{link}')
        else:
            if (word in self.words):
                print('No links')
            else:
                print('No links; word not in dictionary')



    def showWordDiagnostics(self, minWordSize = 1, maxWordSize = 11, characteristic = 'links', order = 'asc'):
        '''For every word that meets the length of int minWordSize, sort them in order with the string characteristic and order as 
        guide. Proper inputs are \"links\", \"alphabet\", \"word_size\" for characteristic, and \"asc\", \"desc\" for order.'''

        presentWordList = [] #Represented as tuple of (word, numLinks)

        #Special functions for sorting
        characteristics = {'links': lambda double: double[1], 'alphabet': lambda double: double[0], 'word_size': lambda double: len(double[0])}

        key = None
        reverse = None

        if (characteristic.lower() in characteristics):
            key = characteristics[characteristic]
        else:
            print('Invalid input.')
            return

        if (order.lower() == 'asc' or order.lower() == 'desc'):
            reverse = order == 'desc'
        else:
            print('Invalid input.')
            return

        for word in self.wordLinks:
            if (len(word) >= minWordSize and len(word) <= maxWordSize):
                presentWordList.append((word, len(self.wordLinks[word])))

        presentWordList.sort(reverse = reverse, key = key)

        for double in presentWordList:
            print(f'{double[0]}\t|\t{double[1]}')



    def showUsedLinks(self):
        '''Pretty prints the values in usedLinks'''

        for link in self.usedLinks:
            print(link)



    def showSearchedSet(self):
        '''Pretty prints the values in searchedSet'''

        for search in self.searchedSet:
            print(search)



    def removeWord(self, word):
        '''Removes a word from both the dictionary and the collection of used links; should only be used on words that have reached
        the "link limit"'''
        
        if (word in self.words):

            lostLinks = None;
            if (word in self.wordLinks):
                lostLinks = self.wordLinks[word] #The links contained inside the word are not to be destroyed
                del self.wordLinks[word] #Word deleted from database
            
            self.words.discard(word) #Word deleted from dictionary ################ FOR SOME REASON, THIS TENDS TO INCREASE THE SIZE OF DICT INITIALLY
            self.tree.remove(word)

            with open('dictionary.p', 'wb') as dictionaryFile: #Write bytes
                pickle.dump(self.words, dictionaryFile) #Save the modified dictionary

            with open(f'deleted_words/{word}.p', 'wb') as wordFile:
                pickle.dump(lostLinks, wordFile) #Save the lost links

            with open('wordLinks.p', 'wb') as wordLinksFile:
                pickle.dump(self.wordLinks, wordLinksFile) #Save the new modified wordLinks
        else:
            print('Word does not exist.')



    def export(self):
        '''Exports the data stored in wordLinks and dictionary into csv files'''

        with open('csv/wordLinks.csv', 'w', encoding = 'utf-8') as csvFile: #Saves wordLinks

            csvFile.write('Word,Link\n') #Order

            i = 0
            counter = 0
            for word in self.wordLinks:
                if (len(self.wordLinks[word]) >= 4 or counter >= 10082):
                    csvFile.write(f'{word},')

                    for link in self.wordLinks[word]:
                        csvFile.write(f'{link}')

                    if (i != len(self.wordLinks) - 1):
                        csvFile.write('\n')
                else:
                    counter += 1
                i += 1


        with open('csv/dictionary.csv', 'w', encoding = 'utf-8') as csvFile: #Saves dictionary OF UTILIZED WORDS ONLY

            csvFile.write('Word,Letter\n')

            i = 0
            for word in self.words:
                if (word in self.wordLinks):
                    if (i == len(self.wordLinks) - 1):
                        csvFile.write(f'{word},{word[0]}')
                    else:
                        csvFile.write(f'{word},{word[0]}\n')
                    i += 1



    def slice(self):
        '''Normalizes wordLinks; sets every word to have an amount of links less than or equal to the max size, as specified'''

        for word in self.wordLinks:
            if (len(self.wordLinks[word]) > self.MAX_LINKS_PER_WORD):
                
                i = 0
                newSet = set()

                for link in self.wordLinks[word]:
                    if (i == self.MAX_LINKS_PER_WORD): #Place maximum amount of links into new set, then stop
                        break
                    newSet.add(link)
                    i += 1
                self.wordLinks[word] = newSet

        with open('wordLinks.p', 'wb') as wordLinksFile:
            pickle.dump(self.wordLinks, wordLinksFile)



    def wordStats(self):
        '''Returns some statistics on the data currently collected, particularly focusing on words'''

        #Completion percentage; words with at least one link
        print('\nPERCENT WORDS COMPLETED (contain at least one link):')

        total = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}
        used = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}

        for word in self.words:
            total[len(word)] += 1
            if (word in self.wordLinks):
                used[len(word)] += 1

        for i in range(2, 12):
            print(f'{i} letters: {used[i]}/{total[i]}, {(used[i] / total[i]) * 100}%')
        print(f'In total, {len(self.wordLinks)}/{len(self.words)} words completed, or {(len(self.wordLinks) / len(self.words)) * 100}%')

        #Starting/ending letters
        print('\nLETTER STATS (used words):')

        starting = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0}
        ending = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0, 'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0, 'z': 0}

        for word in self.wordLinks:
            starting[word[0]] += 1
            ending[word[-1]] += 1

        for letter in starting:
            print(f'Starts with {letter}: {starting[letter]}/{len(self.wordLinks)}, {(starting[letter] / len(self.wordLinks)) * 100}%\t\t\tEnds with {letter}: {ending[letter]}/{len(self.wordLinks)}, {(ending[letter] / len(self.wordLinks)) * 100}%')

        print('\nLETTER STATS (all words):')

        for word in self.words:
            if (word not in self.wordLinks): #Reuses previous dictionaries
                starting[word[0]] += 1
                ending[word[-1]] += 1

        for letter in starting:
            print(f'Starts with {letter}: {starting[letter]}/{len(self.words)}, {(starting[letter] / len(self.words)) * 100}%\t\t\tEnds with {letter}: {ending[letter]}/{len(self.words)}, {(ending[letter] / len(self.words)) * 100}%')

        #Link character statistics
        print('\nLINK CHARACTER COUNT (from all links recorded):')

        characters = {}
        sample_count = 5000 #How many usedLinks to count

        for link in self.usedLinks:
            sample_count -= 1

            for character in link:
                if character not in characters:
                    characters[character] = 0
                characters[character] += 1

            if (sample_count == 0):
                break

        orderedCharacters = list(characters.keys())
        orderedCharacters.sort()

        for character in orderedCharacters:
            print(f'{character}:{characters[character]}')



    def addNewWord(self, word, complex = False):
        '''Adds a new string word to the words set; if complex is specified to be True, this function will iterate through all of the
        values in set usedLinks'''

        if (word in self.words):
            print(f'That word already exists in the dictionary. ({word} in wordLinks with {len(self.wordLinks[word])} recorded links)')
            return

        if (len(word) < 2 or len(word) > 11):
            print('Word entered is either too long or too short to be valid.')
            return

        for c in word:
            if (c < 'a' or c > 'z'): #Not alphabetical
                print('Invalid word entered. Proper words must contain only lowercase alphabetical characters.')
                return

        self.words.add(word)

        with open('dictionary.p', 'wb') as dictionaryFile:
            pickle.dump(self.words, dictionaryFile)

        if (os.path.exists(f'deleted_words/{word}.p')):
            print('Existing backup found. Adding lost links...')

            with open(f'deleted_words/{word}.p', 'rb') as wordFile:
                links = pickle.load(wordFile)
                if (links != None):
                    self.wordLinks[word] = links;

            if (len(self.wordLinks[word]) == 0): #No links found
                del self.wordLinks[word]

            if (len(self.wordLinks[word]) >= self.MAX_LINKS_PER_WORD): #Enough links found
                complex = False #No need to iterate
        
        if (complex): #Add links; wordLinks should only contain the word if at least one link is found

            count = 0
            totalCount = 0
            print('Adding links...')

            for link in self.usedLinks:
                if (word in link.lower()): #Link must be proper before being checked
                    if (word not in self.wordLinks):
                        self.wordLinks[word] = set()
                    else:
                        if (len(self.wordLinks[word]) == self.MAX_LINKS_PER_WORD): #No need in adding anymore links
                            break
                    self.wordLinks[word].add(link)
                    count += 1
                totalCount += 1

            print(f'{count} new links added to {word}')
            print(f'Out of all {len(self.usedLinks)} links recorded, {totalCount} were counted')

        if (word in self.wordLinks):
            with open('wordLinks.p', 'wb') as wordLinksFile:
                pickle.dump(self.wordLinks, wordLinksFile)



            


if (__name__ == '__main__'):

    searcher = youtubeSearcher()


    #################### THIS IS A DUPLICATE OF THE SAVE FUNCTION; IF THE PROGRAM IS INTERRUPTED THIS MAKES SURE FILES ARE SAVED
    def emergencySave():
        '''Panic saves all the data the program has collected to json files; this function should not be called in any other moment
        except for an unexpected exit, as otherwise the program may only save partial information'''

        if (searcher.sync):
            print('\nUSEDLINKS AND WORDLINKS SYNCHRONIZED\n') #"Synchronized" means that the scraped links were saved to both
        else:
            print('\nUSEDLINKS AND WORDLINKS NOT SYNCHRONIZED!\n')

        choice = input('SAVE ALL DATA? (Y/N): ')
        if (choice == 'N'):
            pass
        else:
            with open('searchedSet.p', 'wb') as searchedSetFile:
                pickle.dump(searcher.searchedSet, searchedSetFile)

            with open('wordLinks.p', 'wb') as wordLinksFile:
                pickle.dump(searcher.wordLinks, wordLinksFile)

            with open('usedLinks.p', 'wb') as usedLinksFile:
                pickle.dump(searcher.usedLinks, usedLinksFile)

            print('\nFiles saved\n')



    while (True):
        query = input('\nAccess a word or enter a special command ( /SCRAPE, /DIAG, /WORDS, /REMOVE, /ADDWORD, /EXPORT, /STAT, /EXIT ): ')
        print('\n')
        query = query.strip()

        if (query == ''):
            continue #Try asking for input again

        combinedQuery = query.split(' ') #Allows for variables to be alongside the command
        query = combinedQuery[0]
        combinedQuery = combinedQuery[1:]
        
        if (query == '/SCRAPE'):

            if (len(combinedQuery) > 0): #If multiple commands were entered
                iterations = combinedQuery[0]
            else:
                iterations = input('Enter the amount of iterations you would like to undergo: ')
                print('\n')

            if (iterations == '/BACK'):
                continue
            elif (iterations.isnumeric()): #If the value entered is a number
                iterations = int(iterations)

                if (iterations > 300):
                    confirm = input('This process will take about ' + searcher.calcTime(iterations * searcher.PREDICTED_AVERAGE_ITERATION) + '; do you wish to continue? (y/n): ')
                    print('\n')

                    if (confirm == 'n'):
                        continue

                atexit.register(emergencySave)
                searcher.scrapeLinks(iterations)
                atexit.unregister(emergencySave) #No longer necessary
            elif (iterations == ''): #Default scrape value
                atexit.register(emergencySave)
                searcher.scrapeLinks(1)
                atexit.unregister(emergencySave)
            else:
                print('Invalid input.')

        elif (query == '/DIAG'):
            
            minWordSize = input('Enter the minimum length of the words to be displayed: ')
            print('\n')
            if (minWordSize == '/BACK'): continue
            maxWordSize = input('Enter the maximum length of the words to be displayed: ')
            print('\n')
            if (maxWordSize == '/BACK'): continue
            characteristic = input('Enter what you would like to sort by ( links, alphabet, word_size ): ')
            print('\n')
            if (characteristic == '/BACK'): continue
            order = input('Enter the order you desire ( asc, desc ): ')
            print('\n')
            if (order == '/BACK'): continue

            if (minWordSize.isnumeric()):
                minWordSize = int(minWordSize)
            elif (minWordSize == ''):
                minWordSize = 1
            else:
                print('Invalid input.')
                continue

            if (maxWordSize.isnumeric()):
                maxWordSize = int(maxWordSize)
            elif (maxWordSize == ''):
                maxWordSize = 11
            else:
                print('Invalid input.')
                continue

            if (characteristic == ''): characteristic = 'links'
            if (order == ''): order = 'asc'

            searcher.showWordDiagnostics(minWordSize, maxWordSize, characteristic, order)

        elif (query == '/WORDS'):

            minWordSize = input('Enter the minimum length of the words to be displayed: ')
            print('\n')
            if (minWordSize == '/BACK'): continue
            maxWordSize = input('Enter the maximum length of the words to be displayed: ')
            print('\n')
            if (maxWordSize == '/BACK'): continue

            if (minWordSize.isnumeric()):
                minWordSize = int(minWordSize)
            elif (minWordSize == ''): #Default wordLinks value is 1
                minWordSize = 1
            else:
                print('Invalid input.')

            if (maxWordSize.isnumeric()):
                maxWordSize = int(maxWordSize)
            elif (maxWordSize == ''):
                maxWordSize = 11
            else:
                print('Invalid input.')
                continue

            searcher.showWordLinks(minWordSize, maxWordSize)

        elif (query == '/EXPORT'):

            confirm = input('This process will export a large chunk of data. Would you like to continue? (y/n): ')
            if (confirm == 'y'):
                searcher.export()

        elif (query == '/SLICE'):

            confirm = input('WARNING: This process is not easily reversible. Would you like to continue? (y/n): ')
            if (confirm == 'y'):
                searcher.slice()

        elif (query == '/STAT'):

            searcher.wordStats()

        elif (query == '/REMOVE'):

            word = ''

            if (len(combinedQuery) > 0):
                word = combinedQuery[0]
            else:
                word = input('Enter the word you would like to delete: ')
                print('\n')
            
            if (word == '/BACK'): continue
            if (word == ''): continue

            confirm = input('WARNING: This process is not easily reversible. Would you like to continue? (y/n): ')
            print('\n')
            if (confirm == 'y'):
                searcher.removeWord(word.lower())

        elif (query == '/ADDWORD'):

            word = ''

            if (len(combinedQuery) > 0):
                word = combinedQuery[0]
                combinedQuery = combinedQuery[1:]
            else:
                word = input('Enter the word you would like to add: ')
                print('\n')

            if (word == '/BACK'): continue
            if (word == ''): continue

            if (len(combinedQuery) > 0): #Whether the process is complex
                complex = (combinedQuery[0] == 'y')
            else:
                complex = input('Should the system check through already searched links to find matches? (y/n): ')
                complex = (complex == 'y')
                print('\n')

            confirm = input('WARNING: This process takes a great amount of time. Would you like to continue? (y/n): ')
            print('\n')
            if (confirm == 'y'):
                searcher.addNewWord(word.lower(), complex)

        elif (query == '/EXIT'):
            exit()
        else: #Assumes a word otherwise
            searcher.showLinks(query.lower())
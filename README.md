# TubeWord-Scraper

A YouTube video scraper with a very specific purpose. This tool was made to collect data for the tubeword project (at https://github.com/adldtd/tubeword). In short, it collects video IDs with words in them, by searching random english strings. The program also comes with a command prompt, including analysis and data saving functions.

## Installation

To clone the repo, run `git clone https://github.com/adldtd/TubeWord-Scraper`

Make sure Python (at least 3.9.0) is installed. The only external library the program uses is Python requests (version 2.27.1); this can be installed by running `pip install requests`

The tool comes with a list of words, pickled into "dictionary.p". This list is a modified version of the one found at https://github.com/dwyl/english-words. In order to use your own dictionary, run filter.py on the list, then pickleTheWords.py, and then move the pickled dict into youtubeScraper.
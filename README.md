# Verb Tense Extractor
Natural Language Processing: Extracts words from a given page, translates them to another language and creates a database of all tenses for each.

## About
This script extracts English words (here verbs) from a web page (step 1), translates them to German (step 2), extracts tense information for each German word (step 3) and saves each tense information in a json file (step 4). Each step in detail:
### Step 1
- First we get the list of words from a web page
- Here I got the list of verbs only from https://verbs.colorado.edu/propbank/framesets-english/
- You can get / create a HTML page in the same format
- This HTML structure is used to scrape for words, hence it is important to maintain the same layout

### Step 2
- For each English word, we translate to another language using a Dictionary
- Here, I used [Yandex Dictionary](https://dictionary.yandex.net/api/v1/dicservice.json) to translate English verbs to German
- You can find a similar API which returns translated JSON for your own destination language

### Step 3
- For each translated German word, we extract tense information from a dictionary
- Here I used [Verbix](http://www.verbix.com/webverbix/German/) to get all tenses for each verb
- You can find a similar web page for scarping and creating a JSON of tenses for each verb

### Step 4
- Each JSON is persisted for future use
- Here I saved the tense information of each German verb into a separate file with base64 encoding of the verb for file name

## Installation
Follow these steps to tweek the repo and make it for whatever translation language you want
- Clone the repo
- Install Beautiful Soup python package as shown [here](http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
- You can use existing English verbs taken from this [bank](https://verbs.colorado.edu/propbank/framesets-english/) or use your own. If you use your own, make sure the HTML matches exactly like the bank's and replace with existing propbank.html
- All translated verbs are saved in `verbs.txt` file in the format `translation1,translation2##########synonym_translation1,synonym_translation2`, once per line
- These verbs are used to extract tense information from Verbix like website as explained above in Step 3
- The `main` function has the calls to each step

Each step above is cached into files to prevent network calls in future for next steps.

import pandas as pd
import unicodedata
from collections import Counter
import HebrewStopWords
import re
import regex


def word_count(text):
    word_count = {}
    for word in text.split():
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1
    return word_count


def strip_punctuation(text):
    punctutation_cats = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
    return ''.join(x for x in text
                   if unicodedata.category(x) not in punctutation_cats)
    
    
"""
Iterate over a given column of dictionaries, and return a dictionary,
    that contains all the keys in the previous ones.
"""
def word_count_to_dict(word_count):
    count_all_words = {}
    for d in word_count:
        for k, v in d.items():
            if k not in count_all_words.keys():
                count_all_words[k] = 1
            else:
                count_all_words[k] += 1
    return count_all_words



# Reading the text file
with open('chat_history.txt', encoding='utf8') as f:
    string = f.read()
    
rx = regex.compile(r'''
    (?(DEFINE)
        (?P<date>\d{2}/\d{2}/\d{2},\ \d{2}:\d{2}) # the date format
    )
    ^                    # anchor, start of the line
    (?&date)             # the previously defined format
    (?:(?!^(?&date)).)+  # "not date" as long as possible
''', regex.M | regex.X | regex.S)

content = []
entries = (m.group(0).replace('\n', ' ') for m in rx.finditer(string))
for entry in entries:
    content.append(entry)
    

# Organizing the date
history = history = pd.DataFrame([line.split(" - ", 1) for line in content], columns=['date', 'message'])
history = history.fillna({'message':''})
history = history[~history.message.isin(HebrewStopWords.WhatsApp_stop_words())]


history[['name', 'message']] = history['message'].str.split(' ', n=1, expand=True)
history['name'] = history['name'].str.replace(':','')
history.name = history.name.apply(lambda s: s and re.sub('[^\w\s]', '', s))

# convert to date time
history['date'] = pd.to_datetime(history.date, format='%d/%m/%y, %H:%M', errors='coerce')
history.set_index('date', inplace = True)


# Remove punctuations
history = history.fillna({'message':''})
history['message'] = history['message'].str.replace('<מדיה הושמטה>', 'שיתוף_מדיה')
history['clear_message'] = history['message'].apply(strip_punctuation)

# Delete User's picture and title changes - fix later?
history = history[~history.name.isin({'שינית'})]

names_all = history.name.unique()

history['word_count'] = history.clear_message.apply(word_count)
count_all_words = word_count_to_dict(history['word_count'])
history['total_word_count'] = history['word_count'].apply(lambda x: sum(x.values()))



# A dictionary with the user's history information (dataframe)
dict_name = {}
for name in names_all:
    dict_name[name] = history[history['name'] == name]

# Removing the stop words from the words  
stop_words = HebrewStopWords.getStopWords()
count_all_words_clean = {k: v for k,v in count_all_words.items() if k not in stop_words}

# Top words from each
top_words_each = {}    
top_10_words_each = pd.DataFrame()
for name, dictionary in dict_name.items():
    top_words_each[name] =  word_count_to_dict(dictionary['word_count'])
    top_words_each[name] = {k: v for k,v in top_words_each[name].items() if k not in stop_words}
    top_10_words_each[name] = pd.Series(Counter(top_words_each[name]).most_common(10))
    


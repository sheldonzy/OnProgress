import pandas as pd
import unicodedata
from collections import Counter
import HebrewStopWords, plot_functions
import re
import regex
import emoji

def word_count(text):
    word_count = {}
    for word in text.split():
        if word not in word_count:
            word_count[word] = 1
        else:
            word_count[word] += 1
    return word_count

# Add "?"
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

"""
Returns a dictionary with the top emoji sent by each user
    Argument: top_words_each
"""
def top_3_emoji_users(top_words, top=3):
    emoji_distribution = {}
    for name, df in top_words.items():
        emoji_counter = Counter({i:j for i,j in df.items() if i in emoji.UNICODE_EMOJI})
        emoji_distribution[name] = emoji_counter.most_common(top)
    
    return emoji_distribution


"""
Merge a dictionary it's dictionaries value. for example:
    input: {'first':{'a': 5}, 'second':{'a': 10}, 'third':{'b': 5, 'c': 1}}
    output: {'a': 15, 'b': 5, 'c': 1}
"""
def merge_dicts(large_dictionary):
    return sum(map(Counter, large_dictionary.values()), Counter())

"""
returns a dictionary with the top emoji and the counter.
    Argument: A dictionary with the word count as value (count_all_words)
"""
def top_emoji_all(top_words, top=10):
    return dict(Counter({i:j for i,j in top_words.items() if i in emoji.UNICODE_EMOJI}).most_common(top))



"""
Get a dictionary with the count of emoji usage.
    Argument: (top_words_each) and optional get_top = top (get_top) emoji
"""

def top_emoji_users(top_words, get_top=None):
    top_emoji_dictionary = {}
    for name, dictionary in top_words.items():
        emoji_user_dictionary = {}
        for key, value in dictionary.items():
            if key in emoji.UNICODE_EMOJI:
                emoji_user_dictionary[key] = value
        top_emoji_dictionary[name] = emoji_user_dictionary
    if get_top == None:
        return top_emoji_dictionary
    else:
        for name, dictionary in top_emoji_dictionary.items():
            top_emoji_dictionary[name] = dict(Counter(top_emoji_dictionary[name]).most_common(get_top))
        return top_emoji_dictionary




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
count_all_words = {k: v for k,v in count_all_words.items() if k not in stop_words}

# Top words from each
top_words_each = {}    
for name, dictionary in dict_name.items():
    top_words_each[name] =  word_count_to_dict(dictionary['word_count'])
    top_words_each[name] = {k: v for k,v in top_words_each[name].items() if k not in stop_words}

if __name__ == '__main__':
    # messages per month, choose person
    name = "מוסקו"
    plot_functions.messages_per_month_plot(dict_name[name], name)
    
    # Number of messages per month for all users
    plot_functions.messages_per_month_users_plot(dict_name)
    
    # For a given sentence, calculate the number of times said by user
    sentence = "משפט כלשהו"
    plot_functions.sentence_bar(dict_name, sentence)
    
    #
    word = "מילה"
    plot_functions.word_bar(top_words_each, word)
    
    # longest message by user (counted by number of words)
    plot_functions.longest_message_by_word_plot(dict_name)

    # Longest word by user (counted by the length of the word)
    plot_functions.longest_word_pie(dict_name)
    
    # Distribution of messages by users
    plot_functions.distribution_by_users(dict_name)
    
    # Plot top emoji bar
    plot_functions.plot_top_emoji_bar(top_emoji_all(count_all_words, top=5))
    
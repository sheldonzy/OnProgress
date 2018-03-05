import pandas as pd
import unicodedata
import HebrewStopWords
import re
import regex
import emoji

from collections import Counter

class Analyser:
    
    def __init__(self, path):
        # Reading the text file
        
        with open(path, encoding='utf8') as f:
            string = f.read()
            
        rx = regex.compile(r'''
            (?(DEFINE)
                (?P<date>\d{2}/\d{2}/\d{2},\ \d{2}:\d{2}) # the date format
            )
            ^                    # anchor, start of the line
            (?&date)             # the previously defined format
            (?:(?!^(?&date)).)+  # "not date" as long as possible
        ''', regex.M | regex.X | regex.S)
        
        self.content = []
        entries = (m.group(0).replace('\n', ' ') for m in rx.finditer(string))
        for entry in entries:
            self.content.append(entry)
          
        # Organizing the date
        self.history = pd.DataFrame([line.split(" - ", 1) for line in self.content], columns=['date', 'message'])
        self.history = self.history.fillna({'message':''})
        self.history = self.history[~self.history.message.isin(HebrewStopWords.WhatsApp_stop_words())]
        
        self.history[['name', 'message']] = self.history['message'].str.split(' ', n=1, expand=True)
        self.history['name'] = self.history['name'].str.replace(':','')
        self.history.name = self.history.name.apply(lambda s: s and re.sub('[^\w\s]', '', s))
        
        # convert to date time
        self.history['date'] = pd.to_datetime(self.history.date, format='%d/%m/%y, %H:%M', errors='coerce')
        self.history.set_index('date', inplace = True)

        # Remove punctuations
        self.history.fillna({'message':''}, inplace=True)
        self.history['message'] = self.history['message'].str.replace('<מדיה הושמטה>', 'שיתוף_מדיה')
        self.history['clear_message'] = self.history['message'].apply(self.strip_punctuation)
        
        # Delete User's picture and title changes - fix later?
        self.history = self.history[~self.history.name.isin({'שינית'})]
        self.names_all = self.history.name.unique()
        
        #####
        # counter words and emoji
        self.history['word_count'] = self.history.clear_message.apply(lambda x: Counter(self.emoji_splitter(x)))
        
        self.count_all_words = self.word_count_to_dict(self.history['word_count'])
        self.history['total_word_count'] = self.history['word_count'].apply(lambda x: sum(x.values()))
        
        # A dictionary with the user's history information (dataframe)
        self.dict_name = {}
        for name in self.names_all:
            self.dict_name[name] = self.history[self.history['name'] == name]
        
        # Removing the stop words from the words  
        stop_words = HebrewStopWords.getStopWords()
        self.count_all_words = {k: v for k,v in self.count_all_words.items() if k not in stop_words}
        
        # Top words from each
        self.top_words_each = {}    
        for name, dictionary in self.dict_name.items():
            self.top_words_each[name] =  self.word_count_to_dict(dictionary['word_count'])
            self.top_words_each[name] = {k: v for k,v in self.top_words_each[name].items() if k not in stop_words}



    
    # Add "?"
    def strip_punctuation(self, text):
        punctutation_cats = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
        return ''.join(x for x in text
                       if unicodedata.category(x) not in punctutation_cats)
        
        
    """
    Iterate over a given column of dictionaries, and return a dictionary,
        that contains all the keys in the previous ones.
    """
    def word_count_to_dict(self, word_count):
        count_all_words = {}
        for d in word_count:
            for k, v in d.items():
                if k not in count_all_words.keys():
                    count_all_words[k] = 1
                else:
                    count_all_words[k] += 1
        return count_all_words
    
        
    """
    Count words and
    """
    def emoji_splitter(self, text):
        new_string = ""
        text = text.lstrip()
        if text:
            new_string += text[0] + " "
        for char in ' '.join(text[1:].split()):
            new_string += char
            if char in emoji.UNICODE_EMOJI:
                new_string = new_string + " " 
        return list(map(lambda x: x.strip(), new_string.split()))
    
    
    
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

if __name__ == '__main__':
    pass
    

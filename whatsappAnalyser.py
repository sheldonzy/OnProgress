import pandas as pd
import matplotlib.pyplot as plt
import string
from collections import Counter, defaultdict
from bidi import algorithm as bidialg
import HebrewStopWords
import re
import regex
import emoji
import sys
import dateutil

# This algorithm can catch messages with the following regular expressions
date_patterns = {
"long_datetime" : "(?P<datetime>\d{1,2}\s{1}\w{3}(\s{1}|\s{1}\d{4}\s{1})\d{2}:\d{2})",
"short_datetime" : "(?P<datetime>\d{2}/\d{2}/\d{4},\s{1}\d{2}:\d{2})",
"mmddyyy_datetime" : "(?P<datetime>\d{1,2}/\d{1,2}/\d{2},\s{1}\d{2}:\d{2})"

}
message_pattern = "\s{1}-\s{1}(?P<name>(.*?)):\s{1}(?P<message>(.*?))$"
action_pattern = "\s{1}-\s{1}(?P<action>(.*?))$"
delete_strings = ("You were added", "Messages to this group are now secured with end-to-end encryption. Tap for more info.",
                  "נוספת לקבוצה")
action_strings = {
"created_group": ("created group", "יצר/ה את הקבוצה"),
"change_icon": ("changed this group's icon", "החליף/ה את תמונת קבוצה זו"),
"change_subject": ("changed the subject","החליף/ה את הנושא", "החליף/ה את נושא הקבוצה"),
"added": ("added", "הוסיף/ה"),
"left": ("left", "עזב/ה"),
"removed": ("removed", "הסיר/ה")
}
Media = ("<מדיה הושמטה>", "<Media omitted>")


class ChatElement:
    def __init__(self, datetime, name, message, action):
        self.datetime = datetime
        self.name = name
        self.message = message
        self.action = action


class Chat:
    def __init__(self, filename):
        self.filename = filename

    def open_file(self):
        x = open(self.filename,'r', encoding='utf8')
        y = x.read()
        content = y.splitlines()
        return content
    
    
## Merge and sum given dictionaries
def dsum(*dicts):
    ret = defaultdict(int)
    #add loop for Series of dicts
    for x in dicts:
        for d in x:
            for k, v in d.items():
                ret[k] += v
    return dict(ret)

## Merge and sum dictionary of dectionaries
def dsum_dictionary(dicts):
    ret = defaultdict(int)
    #add loop for Series of dicts
    for x in dicts.values():
        for k, v in x.items():
            ret[k] += v
    return dict(ret)
    
def rotate_xticks(ax, rotate):
    for tick in ax.get_xticklabels():
        tick.set_rotation(rotate)
    
"""
For a given string:
    - remove punctuations
    - return emojis and words counter
"""
    
def split_count(text):
    table = str.maketrans({key: None for key in string.punctuation})
    if text:
        total_emoji = []
        text = text.translate(table)
        data = regex.findall(r'\X', text)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI for char in word):
                total_emoji += [word] # total_emoji is a list of all emojis
        
        # Remove from the given text the emojis
        for current in total_emoji:
            text = text.replace(current, '') 
        if text:
            return Counter(text.split()), Counter(total_emoji)
        else:
            return Counter(), Counter(total_emoji)
    else:
        return Counter(), Counter()

class Parser:
    
    def parse_message(self,str):
        for pattern in map(lambda x:x+message_pattern, date_patterns.values()):
            m = re.match(pattern, str)
            if m:
                return (m.group('datetime'), m.group('name'), m.group('message'), None)

        # if code comes here, message is continuation or action
        for pattern in map(lambda x:x+action_pattern, date_patterns.values()):
            m = re.match(pattern, str)
            if m:
                # message is not an informative action - delete
                if any(delete_string in m.group('action') for delete_string in delete_strings):
                    return (m.group('datetime'), None, m.group('action'),  m.group('action'))

                for action, action_groups in action_strings.items():
                   if any(action_string in m.group('action') for action_string in action_groups):
                       for pattern in map(lambda x: "(?P<name>(.*?))"+x+"((.*?))", action_groups):
                            m_action = re.match(pattern, m.group('action'))
                            if m_action:
                                return (m.group('datetime'), m_action.group('name'), None, action)
                    
                       sys.stderr.write("[failed to capture name from action] - %s\n" %(m.group('action')))
                       return (m.group('datetime'), None, None, m.group('action'))

        #prone to return invalid continuation if above filtering doesn't cover all patterns for messages and actions
        
        return (None, None, str, None)

    def process(self, content):
        messages = []
        for row in content:
            parsed = self.parse_message(row)
            # if current row is continuation of the previous
            if parsed[0] is None:
                messages[-1].message += parsed[2]
            else:
                messages.append(ChatElement(*parsed))
                
        dfs = []
        for m in messages:
            if m.datetime is None:
                print("[failed to add chatelement to dataframe] - %s, %s, %s, %s\n" %(m.datetime, m.name, m.message, m.action))
            else:
                dfs.append((m.name, m.message, m.action, m.datetime))
            
        df = pd.DataFrame(dfs, index=range(1, len(messages)+1), columns=['name','message','action','date_string'])

        df['Time'] = df['date_string'].map(lambda x: dateutil.parser.parse(x))
        df['Day']  = df['date_string'].map(lambda x: dateutil.parser.parse(x).strftime("%a"))
        df['Date'] = df['date_string'].map(lambda x:dateutil.parser.parse(x).strftime("%x"))
        df['Hour'] = df['date_string'].map(lambda x:dateutil.parser.parse(x).strftime("%H"))

        df['media'] = ((df['message'] == '<Media omitted>') | (df['message'] == "<מדיה הושמטה>")).astype(int)
        
        # Remove punctuations, and count all words and emojis for each message
        df['message_counter'], df['emoji_counter'] = zip(*df['message'].apply(lambda x: split_count(x)))
        
        
        df_actions = df[pd.isnull(df['message'])]
        df_messages = df[pd.isnull(df['action'])]
    

        return df_messages, df_actions
    
    
def charts(df):

    ## Create Canvas
    fig = plt.figure(figsize=(18,16))
    plt.title = "Whatsapp Analyser"
    ax1 = plt.subplot2grid((4,6), (0,0), rowspan=1, colspan=2)
    ax2 = plt.subplot2grid((4,6), (0,2), rowspan=1, colspan=2)
    ax3 = plt.subplot2grid((4,6), (0,4), rowspan=1, colspan=2)
    ax4 = plt.subplot2grid((4,6), (1,0), rowspan=1, colspan=2)
    ax5 = plt.subplot2grid((4,6), (1,2), rowspan=1, colspan=2)
    ax6 = plt.subplot2grid((4,6), (1,4), rowspan=1, colspan=2)    
    ax7 = plt.subplot2grid((4,6), (2,0), rowspan=2, colspan=2)
    ax8 = plt.subplot2grid((4,6), (2,2), rowspan=2, colspan=2)
    ax9 = plt.subplot2grid((4,6), (2,4), rowspan=2, colspan=2)


    ## Graph 1
    hours = df.groupby('Hour')['message'].count()
    ## Visualize hours from 7am forward
    hours[7:].append(hours[:7]).plot(ax=ax1,  title ="Hour of Day")
    ax1.set_xticks(list(range(25)))
    ax1.set_xticklabels(list(range(7,25))+list(range(1,7)))
    for label in ax1.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    
    ## Graph 2 - number of messages per day
    df.groupby('Day').count().plot(y="message",ax=ax2, kind='bar', legend = None, title = 'Days', rot=0)
    
    ## Graph 3 - number of messages per name
    groupby_name = df.groupby('name')
    messages_by_name = groupby_name.count()['message']
    names = [bidialg.get_display(name) for name in messages_by_name.index]
    messages_by_name.plot(ax=ax3, kind = 'bar', title = 'Number of messages')
    ax3.set_xticklabels(names)    
    rotate_xticks(ax3, 50)
    
    ## 4th graph - Visualize message by date in weeks.
    df.groupby('Time').count()['message'].resample('M').sum().plot(
            y="message",ax=ax4, legend = None, title = 'Message by Date (in months)')
    
    ## 5th graph - media 
    media = groupby_name.sum()['media']
    ax5 = pd.Series(data=[val for val in media.values]).plot(kind='bar', ax=ax5, title='Media sharing')
    ax5.set_xticklabels(names)
    rotate_xticks(ax5, 50)
    
    ## 6th graph - number of words per name
    top_words_count_name = df_messages.groupby('name')['message_counter'].agg(dsum)
    values = [(name, sum(words.values())) for name, words in top_words_count_name.items()]
    ax6 = pd.Series(data =[val[1] for val in values]).plot(kind='bar', ax=ax6, title = 'Number of words')
    ax6.set_xticklabels(names)
    rotate_xticks(ax6, 50)
    
    ## 7th graph - most used word and emoji per name
    emoji_count_name = df_messages.groupby('name')['emoji_counter'].agg(dsum)
    stop_words = HebrewStopWords.getStopWords()
    top_words_count_name_clean = {name: {k:v for k,v in count.items() if k not in stop_words} for name, count in top_words_count_name.items()}
    top_words = {name: Counter(words).most_common(5) for name, words in top_words_count_name_clean.items()}
    names_length = messages_by_name.__len__()
    names_series = pd.Series(data = [1] * names_length)
    ax7 = names_series.plot(kind='barh', ax=ax7, title='Top 5 words')
    topWordsInStrings = ['         '.join([val[0] for val in current]) for current in top_words.values()]
    for index, p in enumerate(ax7.patches):
        ax7.annotate(bidialg.get_display(topWordsInStrings[index]), (0.05, p.get_y() + p.get_width() / names_length ))
    ax7.set_yticklabels([bidialg.get_display(name) for name in top_words.keys()])
     
    ## 8th graph - top 10 used words 
    top_words_all = Counter(dsum_dictionary(top_words_count_name_clean)).most_common(15)
    top_words_all_series = pd.Series(index=[val[0] for val in top_words_all], data=[val[1] for val in top_words_all])
    ax8 = top_words_all_series.plot(kind='bar', ax=ax8, title='Top words all')
    ax8.set_xticklabels([bidialg.get_display(name[0]) for name in top_words_all])
    rotate_xticks(ax8, 45)
    
    ## 9th graph - top 10 used emoji
    top_emoji = Counter(dsum(emoji_count_name)).most_common(10)
    top_emoji_series = pd.Series(index=[val[0] for val in top_emoji], data=[val[1] for val in top_emoji])
    ax9 = top_emoji_series.plot(kind='bar', ax=ax9, title='Top emojis all')

    for label in ax9.get_xticklabels() :
        label.set_fontproperties("Segoe UI Emoji")
    rotate_xticks(ax9, 55)
    
    # Changing some visuals
    for ax in fig.axes:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    ax7.get_xaxis().set_ticks([])
    ax7.spines['bottom'].set_visible(False)
    plt.subplots_adjust(wspace=0.46, hspace=1)
    plt.show() 
    

if __name__ == '__main__': 
    chat1 = Chat("chat_history.txt") 

    content = chat1.open_file() 

    parser = Parser() 
    df_messages, df_actions = parser.process(content) 
    charts(df_messages)



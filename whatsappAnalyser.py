import re
import sys
import dateutil
import pandas as pd
import matplotlib.pyplot as plt
import string
from collections import Counter, defaultdict
from bidi import algorithm as bidialg


date_patterns = {
#"long_datetime" : "(?P<datetime>\d{1,2}\s{1}\w{3}(\s{1}|\s{1}\d{4}\s{1})\d{2}:\d{2})"
#"short_datetime" : "(?P<datetime>\d{2}/\d{2}/\d{4},\s{1}\d{2}:\d{2})"
"testingonly" : "(?P<datetime>\d{1,2}/\d{1,2}/\d{2},\s{1}\d{2}:\d{2})"

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

class Parser:
    
    ## Merge and sum given dictionaries
    def dsum(self, *dicts):
        ret = defaultdict(int)
        #add loop for Series of dicts
        for x in dicts:
            for d in x:
                for k, v in d.items():
                    ret[k] += v
        return dict(ret)
    
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
        df['Day'] = df['date_string'].map(lambda x: dateutil.parser.parse(x).strftime("%a"))
        df['Date'] = df['date_string'].map(lambda x:dateutil.parser.parse(x).strftime("%x"))
        df['Hour'] = df['date_string'].map(lambda x:dateutil.parser.parse(x).strftime("%H"))

        df['media'] = ((df['message'] == '<Media omitted>') | (df['message'] == "<מדיה הושמטה>")).astype(int)
        
        # Remove punctuations and counter words
        table = str.maketrans({key: None for key in string.punctuation})
        df['message_counter'] = df['message'].apply(lambda x: Counter((x.translate(table)).split()) if x else Counter())
        
        df_actions = df[pd.isnull(df['message'])]
        df_messages = df[pd.isnull(df['action'])]
        
        top_words_count_name = df_messages.groupby('name')['message_counter'].agg(dsum)
        

        return top_words_count_name, df_messages, df_actions
    
    


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
    ax7 = plt.subplot2grid((4,6), (2,0), rowspan=2, colspan = 6)


    ## Create Charts
    ## Graph 1
    hours = df.groupby('Hour')['message'].count()
    ## Visualize hours from 7am forward
    hours[7:].append(hours[:7]).plot(ax=ax1,  title ="Hour of Day")
    ax1.set_xticks(list(range(25)))
    ax1.set_xticklabels(list(range(7,25))+list(range(1,7)))
    for label in ax1.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    
    ## Graph 2
    df.groupby('Day').count().plot(y="message",ax=ax2, kind='bar', legend = None, title = 'Days')
    
    ## Graph 3
    messages_by_name = df.name.value_counts()
    ax3.set_xticklabels([bidialg.get_display(name) for name in messages_by_name.index])
    messages_by_name.plot(ax=ax3, kind = 'bar', title = 'Number of messages')
    
    top_words_count_name = df_messages.groupby('name')['message_counter'].agg(dsum)
    
    # 6th graph
    top_all = {}
    for name, words in top_words_count_name.items():
        top_all[name] = sum(words.values())
    
    ax6.bar(list(top_all.keys()), list(top_all.values()))
    

    # 7th graph - Visualize message by date in weeks.
    df.groupby('Time').count()['message'].resample('W-Sun').sum().plot(
            y="message",ax=ax7, legend = None, title = 'Message by Date (in weeks)')

    plt.subplots_adjust(wspace=0.46, hspace=1)
    plt.show() 
    


if __name__ == '__main__': 
    chat1 = Chat("chat_history.txt") 

    content = chat1.open_file() 

    parser = Parser() 
    top, df_messages, df_actions = parser.process(content) 
    charts(df_messages)
    


        
    


    
    

    


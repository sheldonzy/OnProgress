import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bidi import algorithm as bidialg
from matplotlib.ticker import MaxNLocator


""" 
Plot number of messages per month of The given data frame
"""
def messages_per_month_plot(dateframe, name):
    fig = plt.figure(figsize=(8,5.5))
    ax = fig.add_subplot(111)
    sum_by_month = dateframe.groupby(pd.TimeGrouper("M")).sum()
    sum_by_month['total_word_count'].replace(np.nan, 0, inplace = True)
    ax.plot(sum_by_month.index, sum_by_month.values, label='Words per month')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_title(name[::-1])
    ax.set_xlabel('Months')
    plt.xticks(rotation=45)
    ax.legend(frameon=False)
    
"""
Plot the number of messages per month of the given users in the dictionary
    Argument: dictionary of data frames, and the desired sentence (dict_name)
"""
def messages_per_month_users_plot(dictionary_df):
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    for name, df in dictionary_df.items():
        sum_by_month = df.groupby(pd.TimeGrouper("20D")).sum()
        sum_by_month['total_word_count'].replace(np.nan, 0, inplace = True)
        ax.plot(sum_by_month.index, sum_by_month.values, label=bidialg.get_display(name))
        ax.fill_between(sum_by_month.index, sum_by_month.values.ravel(), 0, alpha=.1)
    ax.legend(frameon=False, prop={'size': 14}, handlelength=5)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)    
    ax.margins(0)
    plt.rcParams['axes.autolimit_mode'] = 'round_numbers'
    plt.rcParams['axes.xmargin'] = 0.
    plt.rcParams['axes.ymargin'] = 0.
    ax.set_title('Number of messages per user', fontsize=20)
    plt.xticks(rotation=30)
    
"""
Plot a bar graph of the number of times each wrote the given word
    Argument: dictionary of dictionaries of the words and their counts, and the desired word (top_words_each)
"""
def word_bar(dictionaries, word):
    word_dictionary = {}
    names = []
    fig = plt.figure(figsize=(12,8))
    fig.suptitle("How many times you said\n{0}".format(bidialg.get_display(word)), fontsize=20)
    ax = fig.add_subplot(111)
    for name, dictionary in dictionaries.items():
        word_dictionary[name] = dictionary.get(word, 0)
        names.append(str(name))
    names = [bidialg.get_display(i) for i in names]
    ax.bar(names, word_dictionary.values())
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)   

"""
How many times the group said the given sentence.
    Argument: dictionary of data frames, and the desired sentence (dict_name)
"""

def sentence_bar(dictionaries, sentence):
    word_dictionary = {}
    names = []
    fig = plt.figure(figsize=(12,8))
    fig.suptitle("How many times you said\n{0}".format(bidialg.get_display(sentence)), fontsize=20)
    ax = fig.add_subplot(111)
    for name, df in dictionaries.items():
        word_dictionary[name] = df.clear_message.str.count(sentence).sum()
        names.append(str(name))
    names = [bidialg.get_display(i) for i in names]
    ax.bar(names, word_dictionary.values())
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)   
          
    
"""
plot a pie of the longest sentences by names
Argument: dict_names = dictionary with a dataframe for each name
"""
def longest_message_by_word_plot(dict_names):
    plt.figure(figsize=(8,6))
    plt.suptitle('Longest message counter', fontsize=20)
    longest_word_dict = {}
    for name, df in dict_names.items():
        longest_word_dict[name] = df.total_word_count.max()
    labels = [bidialg.get_display(i) for i in list(longest_word_dict.keys())]
    plt.pie(list(longest_word_dict.values()), labels=labels)
    plt.show()
    
    
"""
Plot a pie of the longest words by names
Argument: dict_names = dictionary with a dataframe for each name
"""
def longest_word_pie(dictionary_names):
    plt.figure(figsize=(8,6))
    plt.suptitle('Length of the longest word', fontsize=20)
    longest_word = {}
    for name, df in dictionary_names.items():
        longest_word[name] = df.clear_message.map(len).max()
    patches, texts = plt.pie(list(longest_word.values()))
    labels = [bidialg.get_display(i) for i in list(longest_word.keys())]
    plt.legend(patches, labels, fontsize=8, loc='upper right', frameon=False, prop={'size': 9})
    plt.show()
    
"""
Plot a pie of the distribution of messages by the users
    Argument: (dict_name)
"""
def distribution_by_users(dictionaries):
    plt.figure(figsize=(8,6))
    plt.suptitle('Distribution of messages by the users', fontsize=20)
    distribution = {}
    for name, df in dictionaries.items():
        distribution[name] = len(df.index)
    names_list, values_list = [bidialg.get_display(i) for i in distribution.keys()], list(distribution.values())
    plt.pie(values_list, autopct='%1.1f%%', labels=names_list, explode=tuple([0.02] * len(names_list)))
    
"""
plot a bar chart with the top emoji
    Argument: a dictionary with the top emojis like - (top_emoji_all(count_all_words, top=5))
"""
def plot_top_emoji_bar(top_emoji):
    ax = plt.subplot(111)
    ax.bar(range(1,6), top_emoji.values())
    for label, x, y in zip(top_emoji.keys(), range(1,6), top_emoji.values()):
        plt.annotate(
            label, xy=(x, y), xytext=(10,10),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', alpha=0),
            fontname='Segoe UI Emoji',
            fontsize=20)
    [ax.spines[i].set_visible(False) for i in ['right', 'top']]
    ax.set_xticks([])
    plt.show()
    
"""

    Argument: top_emoji_users(top_words_each, 3)
"""   
def top_emoji(top):
    fig, ax = plt.subplots(figsize=(8, 5))
    y = 9
    level = 0
    for level, top_each in enumerate(top.items()):
        ax.text(9, y - level, bidialg.get_display(top_each[0]), fontsize=20)
        for x, emoj in enumerate(top_each[1].keys(), 3):
            ax.text(9 - x, y - level, emoj, fontname='Segoe UI Emoji', fontsize=20)

    ax.axis([0, 10, 0, 10])
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.axis('off')
    plt.show()


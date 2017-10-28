import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

""" 
Plot number of messages per month of The given data frame
"""
def messages_per_month_plot(dateframe):
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
"""
def messages_per_month_users_plot(dictionary_df):
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    for name, df in dictionary_df.items():
        sum_by_month = df.groupby(pd.TimeGrouper("20D")).sum()
        sum_by_month['total_word_count'].replace(np.nan, 0, inplace = True)
        ax.plot(sum_by_month.index, sum_by_month.values, label=name[::-1])
        ax.fill_between(sum_by_month.index, sum_by_month.values.ravel(), 0, alpha=.5)
    ax.legend(frameon=False, prop={'size': 12})
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)    
    ax.title('Number of messages per user')
    plt.xticks(rotation=30)
    
"""
Plot a bar graph of the number of times each wrote the given word
"""
def word_bar(dictionaries, word):
    word_dictionary = {}
    names = []
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    for name, dictionary in dictionaries.items():
        word_dictionary[name] = dictionary.get(word, 0)
        names.append(str(name))
    names = [name[::-1] for name in names]
    ax.bar(names, word_dictionary.values())
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)   

# dict_name
def sentence_bar(dictionaries, sentence):
    word_dictionary = {}
    names = []
    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    for name, df in dictionaries.items():
        word_dictionary[name] = df.clear_message.str.count(sentence).sum()
        names.append(str(name))
    names = [name[::-1] for name in names]
    ax.bar(names, word_dictionary.values())
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)         
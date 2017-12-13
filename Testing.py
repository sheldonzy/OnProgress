import whatsapp_analysis, plot_functions

if __name__ == '__main__':
    analyser = whatsapp_analysis.Analyser()
    name = "מוסקו"
    plot_functions.messages_per_month_plot(analyser.dict_name[name], name)
    
    # Number of messages per month for all users
    plot_functions.messages_per_month_users_plot(analyser.dict_name)
    
    # For a given sentence, calculate the number of times said by user
    sentence ="כל הזין"
    plot_functions.sentence_bar(analyser.dict_name, sentence)
    
    #
    word = "מילה"
    plot_functions.word_bar(analyser.top_words_each, word)
    
    # longest message by user (counted by number of words)
    plot_functions.longest_message_by_word_plot(analyser.dict_name)

    # Longest word by user (counted by the length of the word)
    plot_functions.longest_word_pie(analyser.dict_name)
    
    # Distribution of messages by users
    plot_functions.distribution_by_users(analyser.dict_name)
    
    # Plot top emoji bar
    plot_functions.plot_top_emoji_bar(whatsapp_analysis.top_emoji_all(analyser.count_all_words, top=5))
    
    # plot top 3 emoji per user
    plot_functions.top_emoji(whatsapp_analysis.top_emoji_users(analyser.top_words_each, 3))



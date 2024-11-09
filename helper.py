import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter


def get_stats(df, selected_user):
    # modify dataframe according to user
    # if user then modify else if 'Overall' then keep entire dataframe
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # number of messages
    num_messages = df.shape[0]

    # number of words
    num_words = df['message'].str.split().apply(lambda x: len(x))
    num_words = num_words.sum()

    # media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # links
    extractor = URLExtract()
    urls = []
    for message in df['message']:
        urls.extend(extractor.find_urls(message))    # extend dont append
    num_links = len(urls)

    return num_messages, num_words, num_media_messages, num_links


def get_most_busy_users(df):
    temp = df[df['user'] != 'Group Notification']    # excluding group notifs
    temp = temp['user'].value_counts()[:10]
    temp_df = temp.reset_index()                     # contains columns user and count

    return temp_df


# removing stopwords and other preprocessing
def preprocess_messages(df):
    # removing media messages
    df = df[df['message'] != '<Media omitted>\n']

    # removing stopwords
    f = open('stopwords_hinglish.txt', 'r')
    stopwords = f.read()

    def remove_stopwords(message):
        new_word_list = []
        for word in message.lower().split():           # don't forget to convert to lower first as the stopwords are in lower (lots of other reasons also)
            if word not in stopwords:
                new_word_list.append(word)

        return new_word_list

    temp = df['message'].apply(remove_stopwords)
    temp = temp.apply(lambda x: ' '.join(x))
    message_string = temp.str.cat(sep=' ')             # concatenates all the strings in the series / dataframe

    return message_string


def get_wordcloud(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    message_string = preprocess_messages(df)

    wordcloud = WordCloud(width=700,
                          height=500,                  # increase height and width for better resolution
                          min_font_size=2,
                          max_font_size=100,
                          max_words=150,
                          background_color="black",
                          margin=10,
                          colormap='viridis')
    wordcloud = wordcloud.generate(message_string)

    return wordcloud


def get_most_frequent_words(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    message_string = preprocess_messages(df)

    message_string_list = message_string.split()         # split without any arguments takes into account \n, \t as well
    counts = Counter(message_string_list)
    count_df = pd.DataFrame({'word': counts.keys(), 'count': counts.values()})
    count_df = count_df.sort_values(by='count', ascending=False)
    most_frequent_words = count_df[:10]                  # taking top 10 values

    return most_frequent_words

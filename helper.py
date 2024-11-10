import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
from emoji import is_emoji


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

# Most Busy Users
def get_most_busy_users(df):
    temp = df[df['user'] != 'Group Notification']    # excluding group notifs
    temp = temp['user'].value_counts()
    temp_df = temp.reset_index()                     # contains columns user and count

    return temp_df


# -- Most Frequent Words --

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

    wordcloud = WordCloud(width=1000,
                          height=600,                  # increase height and width for better resolution
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


# -- Emoji Analysis --
def get_emoji_counts(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    message_string = preprocess_messages(df)

    emojis = []
    for ch in message_string:
        if is_emoji(ch):
            emojis.append(ch)

    emoji_count = Counter(emojis)
    emoji_count_df = pd.DataFrame({'emoji': emoji_count.keys(), 'count': emoji_count.values()})
    emoji_count_df = emoji_count_df.sort_values(by='count', ascending=False)

    return emoji_count_df


# -- Activity Time Series --
def get_month_and_day_time_series(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    month_df = df.groupby(['year', 'month', 'month_num'], as_index=False)['message'].count()
    # month and month_num will be grouped the same so no problem (month_num just need for sorting)
    month_df['month_year'] = month_df['month'] + '-' + month_df['year'].astype(str)
    month_df = month_df.sort_values(by=['year', 'month_num'])                                   # sorting on year then on month_num

    df['date_temp'] = df['date'].dt.date
    day_df = df.groupby('date_temp', as_index=False)['message'].count()

    return month_df, day_df


# -- Activity Map --
def get_activity_map(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    day_df = df.groupby('day_name', as_index=False)['message'].count()

    # making day_name an ordered column
    # cannot use day_num for sorting as day number != day name always
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_df['day_name'] = pd.Categorical(day_df['day_name'], categories=day_order, ordered=True)
    day_df = day_df.sort_values('day_name').reset_index(drop=True)      # Sort the DataFrame by the custom order

    month_df = df.groupby(['month', 'month_num'], as_index=False)['message'].count()
    month_df = month_df.sort_values(by='month_num')

    return day_df, month_df


# heatmap
# def get_activity_heatmap(df, selected_user):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     heatmap = df.pivot_table(index='day_name', columns='hour_period', values='message', aggfunc='count').fillna(0)
#
#     return heatmap


# better function - gets the sorted index and column heatmap
def get_activity_heatmap(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # creating the sorted heatmap
    # sorting days (index)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_name'] = pd.Categorical(df['day_name'], categories=day_order, ordered=True)

    # Pivot table as before
    heatmap = df.pivot_table(index='day_name', columns='hour_period', values='message', aggfunc='count').fillna(0)

    # Sort hours (columns)
    # Ensure 'hour_period' is in the correct order (0-1, 1-2, ..., 23-24)
    hour_order = [f"{i}-{i+1}" for i in range(24)]

    # Fill missing hour periods with zero values - certain chats have no messages on certain hours at all the days. So pivot table excludes those columns alltogether. It isn't even fixed in fillna(0) while creating the table as the column itself is not present as no text on that hour on any of the days
    # reindex is a method used with pandas DataFrames and Series. It allows you to change the row/column labels or align your data to a new set of labels (index or columns). If you have missing rows or columns, reindex can fill them with a specified value (like NaN or 0).
    heatmap = heatmap.reindex(columns=hour_order, fill_value=0)

    # Reorder columns to match the desired hour order
    heatmap = heatmap[hour_order]

    return heatmap

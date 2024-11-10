import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import time


# my libraries
from preprocessor import preprocess_data    # also imports the imports present in preprocessor.py automatically
import helper


st.set_page_config(page_title="Ree Whatsapp Chat Analyzer",
                   page_icon=None,
                   layout="wide")

st.sidebar.title('Whatsapp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader(label="Upload the Exported Chat",
                                         type='txt',
                                         help='Upload the Exported Chat. The chat should be exported without media. The file should be of the form chat.txt')

if uploaded_file:
    # preprocess data
    bytes_data = uploaded_file.getvalue()       # bytes data
    string_data = bytes_data.decode("utf-8")    # convert bytes data to string data (into a string basically)
    df = preprocess_data(string_data)

    # select a user
    users = df['user'].unique().tolist()       # converting to list for easier processing (could have done with numpy array ass well no big deal)
    users.sort()
    users.insert(0, 'Overall')                 # inserting 'Overall' at index 0 for overall analysis

    selected_user = st.sidebar.selectbox(
        "Select User",
        users,
    )

    # click to start analysis on the selected user
    if st.sidebar.button("Show Analysis"):
        # # progress bar
        # progress_text = "Analyzing. Please wait."
        # my_bar = st.progress(0, text=progress_text)
        #
        # for percent_complete in range(100):
        #     time.sleep(0.005)
        #     my_bar.progress(percent_complete + 1, text=progress_text)
        # time.sleep(1)
        # my_bar.empty()

        st.title(f'Selected User : :blue[{selected_user}]')
        st.divider()

        # -- Chat statistics --
        st.title(':red[Chat Statistics]')
        num_messages, num_words, num_media_messages, num_links = helper.get_stats(df, selected_user)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages", anchor=False)
            st.subheader(num_messages)
        with col2:
            st.header("Total Words", anchor=False)
            st.subheader(num_words)
        with col3:
            st.header("Media Shared", anchor=False)
            st.subheader(num_media_messages)
        with col4:
            st.header("Links Shared", anchor=False)
            st.subheader(num_links)

        # -- most busy users --
        st.divider()
        if selected_user == 'Overall':
            st.title(':red[Most Busy Users]')
            busy_users_df = helper.get_most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:

                busy_users_top_10 = busy_users_df[:10]
                fig = px.bar(busy_users_top_10,
                             x='user',
                             y='count',
                             labels={
                                 'user': 'User',
                                 'count': 'Number of Messages'
                             },
                             title='Most Busy Users')

                st.plotly_chart(fig, key="Busy Users", on_select="rerun")

            with col2:
                # pie chart for top 5 most busy users

                # set emojis that occur less than 5% of the times to 'Others'
                threshold = busy_users_df['count'].sum() * 0.05
                busy_users_df['user'] = busy_users_df['user'].where(busy_users_df['count'] > threshold, 'Others')
                busy_users_df = busy_users_df.groupby('user', as_index=False)['count'].sum()    # combining the 'Others' values into one row

                fig = px.pie(busy_users_df, values='count', names='user', title='Top Contributors to Chat')

                st.plotly_chart(fig, key="Top Contributors to Chat", on_select="rerun")

        # -- Activity Time Series Analysis --

        # month wise
        st.divider()
        st.title(':red[Activity Over Time]')
        month_df, day_df = helper.get_month_and_day_time_series(df, selected_user)

        fig = px.line(month_df,
                      x='month_year',
                      y='message',
                      labels={
                          'month_year': 'Month',
                          'message': 'Number of Messages'
                      },
                      title='Month-wise Activity')

        st.plotly_chart(fig)

        # day wise
        fig = px.line(day_df,
                      x='date_temp',
                      y='message',
                      labels={
                          'date_temp': 'Date',
                          'message': 'Number of Messages'
                      },
                      title='Day-wise Activity')

        st.plotly_chart(fig)

        # -- Activity Map --
        st.divider()
        st.title(':red[Activity Map]')
        day_df, month_df = helper.get_activity_map(df, selected_user)

        col1, col2 = st.columns(2)

        with col1:
            # activity map for months
            fig = px.bar(month_df,
                         x='month',
                         y='message',
                         labels={
                             'month': 'Month',
                             'message': 'Activity'
                         },
                         title='Most Active Months')

            st.plotly_chart(fig, key="Most Active Months", on_select="rerun")

        with col2:
            # Activity map for days
            fig = px.bar(day_df,
                         x='day_name',
                         y='message',
                         labels={
                             'day_name': 'Day',
                             'message': 'Activity'
                         },
                         title='Most Active Days',
                         color_discrete_sequence=['#FF4B4B']*7)

            st.plotly_chart(fig, key="Most Active Days", on_select="rerun")

        # Activity heatmap
        st.divider()
        st.subheader('Heatmap')
        heatmap = helper.get_activity_heatmap(df, selected_user)
        # fig, ax = plt.subplots()
        # sns.heatmap(heatmap)
        # st.pyplot(fig)

        import plotly.graph_objects as go

        fig = go.Figure(data=go.Heatmap(
            z=heatmap,
            x=heatmap.columns,
            y=heatmap.index,
            colorscale='ice'))

        fig.update_layout(xaxis_nticks=gi)     # to display all the ticks
        st.plotly_chart(fig)

        # -- Wordcloud and Most Frequently Used Words --
        st.divider()
        st.title(':red[Most Frequent Words]')
        wordcloud = helper.get_wordcloud(df, selected_user)
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(15, 15))
            ax.imshow(wordcloud)
            ax.axis("off")

            st.caption('Wordcloud')
            st.pyplot(fig)

        with col2:
            most_frequent_words = helper.get_most_frequent_words(df, selected_user)
            fig = px.bar(most_frequent_words,
                         x='word',
                         y='count',
                         labels={
                             'word': 'Word',
                             'count': 'Count'
                         })

            st.caption('Most Frequent Words')
            st.plotly_chart(fig, key="Most Frequent Words", on_select="rerun")

        # entire dataframe
        # st.caption('Word Counts')
        # st.dataframe(most_frequent_words, height=300, use_container_width=True)

        # -- Emoji Analysis --
        st.divider()
        st.title(':red[Emoji Analysis]')
        emoji_count_df = helper.get_emoji_counts(df, selected_user)

        col1, col2 = st.columns(2)

        with col1:
            # bar chart of top 10 emojis
            fig = px.bar(emoji_count_df[:10],
                         x='emoji',
                         y='count',
                         labels={
                             'emoji': 'Emoji',
                             'count': 'Count'
                         },
                         title='Top 10 Emojis')

            st.plotly_chart(fig, key="Top 10 Emoji Bar Chart", on_select="rerun")

        with col2:
            # pie chart for most used emojis
            # set emojis that occur less than 2% of the times to 'Others'
            threshold = emoji_count_df['count'].sum() * 0.02
            emoji_count_df['emoji'] = emoji_count_df['emoji'].where(emoji_count_df['count'] > threshold, 'Others')
            emoji_count_df = emoji_count_df.groupby('emoji', as_index=False)['count'].sum()    # combining the 'Others' values into one row

            fig = px.pie(emoji_count_df, values='count', names='emoji', title='Emoji Contriubtion')

            st.plotly_chart(fig, key="Top Emojis Pie chart", on_select="rerun")

        # entire dataframe
        # st.caption('Emoji Counts')
        # st.dataframe(emoji_count_df, height=300, use_container_width=True)




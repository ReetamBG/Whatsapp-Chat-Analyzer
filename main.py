import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

# my libraries
from preprocessor import preprocess_data    # also imports the imports present in preprocessor.py automatically
import helper


st.set_page_config(page_title="Ree Whatsapp Chat Analyzer",
                   page_icon=None,
                   layout="wide")

st.sidebar.title('Whatsapp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader(label="Upload the Exported Chat",
                                         type='txt',
                                         help='Upload the Exported Chat. It should be of the form chat.txt')

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
        st.caption(f'Selected User : {selected_user}')

        # -- Chat statistics --
        st.title('Chat Statistics')
        num_messages, num_words, num_media_messages, num_links = helper.get_stats(df, selected_user)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.subheader(num_messages)
        with col2:
            st.header("Total Words")
            st.subheader(num_words)
        with col3:
            st.header("Media Shared")
            st.subheader(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.subheader(num_links)

        # -- most busy users --
        st.title('Most Busy Users')
        busy_users_df = helper.get_most_busy_users(df)
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(busy_users_df,
                         x='user',
                         y='count',
                         labels={
                             'user': 'User',
                             'count': 'Number of Messages'
                         })

            st.plotly_chart(fig, key="Busy Users", on_select="rerun")

        with col2:
            # pie chart for top 5 most busy users
            busy_users_top_5 = busy_users_df[:5]
            fig = px.pie(busy_users_top_5, values='count', names='user')
            st.plotly_chart(fig, key="Busy Users Top 5", on_select="rerun")

        # -- wordcloud and most frequently used words --
        st.title('Most Frequent Words')
        wordcloud = helper.get_wordcloud(df, selected_user)
        col1, col2 = st.columns(2)

        with col1:
            # fig, ax = plt.subplots(frameon=False)    # frameon=False - removes white border/frame around the pic
            # ax.imshow(wordcloud)
            # ax.axis("off")
            # st.pyplot(fig)
            fig = px.imshow(wordcloud)
            fig.update_xaxes(showticklabels=False)
            fig.update_yaxes(showticklabels=False)
            st.plotly_chart(fig)    # using matplotlib doesnt match with other figures as they are done with plotly

        with col2:
            most_frequent_words = helper.get_most_frequent_words(df, selected_user)
            fig = px.bar(most_frequent_words,
                         x='word',
                         y='count',
                         labels={
                             'word': 'Word',
                             'count': 'Count'
                         })

            st.plotly_chart(fig, key="Most Frequent Words", on_select="rerun")




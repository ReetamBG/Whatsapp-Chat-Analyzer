# import here not in main.py as it will automatically import these imports there when we import anything from here
import pandas as pd
import re


def preprocess_data(data):

    data = data.replace("\u202f", " ")
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[AP]M\s-\s'

    # extracting message and date
    date = re.findall(pattern, data)
    messages = re.split(pattern, data)[1:]
    df = pd.DataFrame({'messages' : messages, 'date' : date})

    # extracting date info
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %I:%M %p - ')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # added later
    df['month_num'] = df['date'].dt.month
    df['day_name'] = df['date'].dt.day_name()

    # extracting user and message
    users = []
    messages = []
    pattern = r'([\w\W]+?):\s'
    for message in df['messages']:
        user = re.findall(pattern, message)
        user_message = re.split(pattern, message)
        if user:
            users.append(user[0])
            messages.append(user_message[2])
        else:
            users.append('Group Notification')
            messages.append(user_message[0])

    df['user'] = users
    df['message'] = messages

    # removing group notifications
    df = df[df['user'] != 'Group Notification']

    df.drop(columns='messages', inplace=True)

    return df

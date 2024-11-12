# import here not in main.py as it will automatically import these imports there when we import anything from here
import pandas as pd
import re


def preprocess_data(data):

    data = data.replace("\u202f", " ")
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s(?:[01]?\d|2[0-3]):[0-5]\d(?:\s[APap][Mm])?\s-\s'    # checks for all cases AM/PM, am/pm and for 24hour formats as well

    # extracting message and date
    date = re.findall(pattern, data)
    messages = re.split(pattern, data)[1:]
    df = pd.DataFrame({'messages': messages, 'date': date})

    # check for all formats of dates
    formats = [
        # 12-hour formats
        '%m/%d/%y, %I:%M %p - ',    # MM/DD/YY 12hrs
        '%d/%m/%y, %I:%M %p - ',    # DD/MM/YY 12hrs
        '%m/%d/%Y, %I:%M %p - ',    # MM/DD/YYYY 12hrs
        '%d/%m/%Y, %I:%M %p - ',    # DD/MM/YYYY 12hrs

        # 24-hour formats
        '%m/%d/%y, %H:%M - ',       # MM/DD/YY 24hrs
        '%d/%m/%y, %H:%M - ',       # DD/MM/YY 24hrs
        '%m/%d/%Y, %H:%M - ',       # MM/DD/YYYY 24hrs
        '%d/%m/%Y, %H:%M - ',       # DD/MM/YYYY 24hrs

        # Additional Formats
        '%Y/%m/%d, %I:%M %p - ',    # YYYY/MM/DD 12hrs
        '%Y/%m/%d, %H:%M - ',       # YYYY/MM/DD 24hrs
    ]

    temp = None
    for fmt in formats:
        temp = pd.to_datetime(df['date'], format=fmt, errors='coerce')
        if temp.notnull().all():  # Break if all dates are parsed successfully (i.e when no coerce happens i.e no null values)
            break
    df['date'] = temp

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # added later
    df['month_num'] = df['date'].dt.month
    df['day_name'] = df['date'].dt.day_name()
    df['hour_period'] = df['hour'].astype(str) + '-' + (df['hour']+1).astype(str)

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

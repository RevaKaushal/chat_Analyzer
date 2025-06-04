import re
import pandas as pd

def preprocess(data):
    pattern = '\[\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}:\d{2}\u202f[APMapm]{2}\]\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Example raw column with timestamps
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # STEP 1: Clean the timestamp
    df['message_date'] = (
        df['message_date']
        .str.replace(r'[\[\]]', '', regex=True)  # Remove square brackets
        .str.replace('\u202f', ' ')  # Replace narrow no-break space with normal space
        .str.strip()  # Strip leading/trailing whitespace
    )

    # STEP 2: Confirm cleaned format looks like this: "25/03/25, 1:06:42 PM"
    # Optional: print few rows to verify
    # print(df['message_date'].head())

    # STEP 3: Parse to datetime safely
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        format='%d/%m/%y, %I:%M:%S %p',
        errors='raise'  # Can also use 'coerce' to silently fail and set NaT
    )

    # STEP 4: Rename for clarity
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # separate users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)  # ^(.+?):\s
        if entry[1:]:  # user name
            # If split successful, we get 3 parts: ['', user, message] ->not working cuz colon is coming even in group notifications
            # if len(entry) == 3:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # ✅ Step 3: (NEW) Refine group_notification using keywords
    def is_group_notification(msg):
        keywords = [
            "created group",
            "added",
            "removed",
            "changed the subject",
            "changed the group icon",
            "Messages and calls are end-to-end encrypted"
        ]
        return any(keyword in msg for keyword in msg.lower() for keyword in keywords)

    # Apply correction
    df['user'] = df.apply(lambda row: 'group_notification' if is_group_notification(row['message']) else row['user'],
                          axis=1)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
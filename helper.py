from urlextract import URLExtract
extract= URLExtract()
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

def fetch_stats(selected_user,df):

    if selected_user !='Overall':
        df= df[ df['user']==selected_user] #df['user']==selected_user--> we'll get specific user dataframe
    num_msg=df.shape[0]#fetching number of messages

    words=[] #fetch total number of words
    for msg in df['message']:
        words.extend(msg.split())

    #df['message'] == '<Media omitted>/n' ->let it be x,give us rows where rows of message column is media
    #df[x].shape[0] gives zero index of shape output as (no.of row,col)
    #num_media= df[ df['message']=='image omitted\n' ].shape[0] #number of media messages
    num_media = df[df['message'].str.contains('omitted', case=False, na=False)].shape[0]

    #fetch number of links shared
    links=[]
    for msg in df['message']:
        links.extend(extract.find_urls(msg))

    return num_msg, len(words),num_media,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'count':'percent'})
    return x,df

def create_wordcloud(selected_user,df):
    if selected_user !='Overall':
        df=df[df['user']==selected_user]
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):
    f=open('stop_hinglish.txt','r')
    stop_words=f.read()
    if selected_user !='Overall':
        df=df[df['user']==selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[~temp['message'].str.contains('omitted', case=False, na=False)&
                ~temp['message'].str.contains('<This message was edited>', case=False, na=False)]
    words = []
    for msg in temp['message']:
        for word in msg.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df= pd.DataFrame(Counter(words).most_common(20))  # top 20 most used words
    return most_common_df

#analysing emojis use now
def emoji_helper(selected_user,df):
    if selected_user!= 'Overall':
        df= df[df['user']==selected_user]
    emojis = []
    for msg in df['message']:
        emojis.extend([c for c in msg if emoji.is_emoji(c)])
    emoji_df=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

#timeline analysis
def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def dailytimeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline
def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
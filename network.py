
# coding: utf-8

# In[1]:


import os
import re
import json
import math
import pickle
import numpy as np
import pandas as pd
import datetime as dt
import multiprocessing as mp
from tqdm import tqdm
from multiprocessing import Pool
from datetime import timezone
from datetime import timedelta
from pprint import pprint
import networkx as nx


# In[2]:


import config
from config import load_tweets_dataframe
from config import dump_tweets_dataframe
from config import load_users_dataframe
from config import dump_users_dataframe
from config import load_friends_dictionary
from config import dump_friends_dictionary
from config import load_needcrawl_set
from config import dump_needcrawl_set
from config import load_newcrawl_dictionary
from config import dump_newcrawl_dictionary
from config import dump_networkx_all
from config import dump_networkx_friends
from config import dump_networkx_potential


# In[3]:


calculate_uniquetweets = config.settings['calculate']['uniquetweets']
calculate_uniqueusers = config.settings['calculate']['uniqueusers']
calculate_network = config.settings['calculate']['network']
calculate_analysis = config.settings['calculate']['analysis']
calculate_friends = config.settings['calculate']['friends']

file_input_path = config.settings['path']['twitter']
dates = config.settings['data']['dates']
search_phrases = config.settings['data']['phrases']
timeframe = config.settings['timeframe']
project_name = config.settings['data']['eventname']
starttime = config.settings['data']['starttime']


# In[4]:


def order_and_reindex(df, column):
    df = df.sort_values(by=[column])
    df = df.set_index(np.arange(len(df.index)))
    return df


# # Unique Tweets

# In[5]:


def convert_utc_to_est(time_string):
    datetime_object = dt.datetime.strptime(time_string, '%a %b %d %H:%M:%S %z %Y')
    return datetime_object.replace(tzinfo=timezone.utc).astimezone(tz=timezone(-timedelta(hours=5)))

def get_created_at(tweet):
    return convert_utc_to_est(tweet['created_at'])

def get_retweet_id(tweet):
    if (tweet['text'].split()[0] == 'RT'):
        user_name = tweet['text'].split()[1][1:-1]
        mentions = tweet['entities']['user_mentions']
        for mention in mentions:
            if mention['screen_name'] == user_name:
                return string_to_int(mention['id'])

def get_reply_id(tweet):
    return string_to_int(tweet['in_reply_to_user_id_str'])
    
def get_user_mentions(tweet):
    retweet_id = get_retweet_id(tweet)
    reply_id = get_reply_id(tweet)  
    mentions = []
    for mention in tweet['entities']['user_mentions']:
        mention_id = string_to_int(mention['id'])
        if mention_id != retweet_id and mention_id != reply_id:
            mentions.append(mention_id)
    return mentions

def string_to_int(string):
    if string is None:
        return None
    else:
        return int(string)

def find_unique_tweets_crawled():
    file_path_dict = {
        date: ['{}/{}_{}.json'.format(file_input_path, x, date) for x in search_phrases]
        for date in dates
    }
    tweets_crawled_list = []
    for date, file_path_list in file_path_dict.items():
        for file_path in file_path_list:
            if (os.path.isfile(file_path)):
                with open(file_path, 'r') as file:
                    counter = 0
                    for line in file.readlines():
                        tweets_crawled_list.append(json.loads(line))
                        counter += 1
                    print('{}, {}, {}'.format(date, file_path, counter))
    
    unique_tweets = list({each['id']:each for each in tweets_crawled_list}.values())
    
    df = pd.DataFrame()
    df['user'] = list(map(lambda tweet: tweet['user']['screen_name'], unique_tweets))
    df['user_id'] = list(map(lambda tweet: string_to_int(tweet['user']['id_str']), unique_tweets))
    df['created_at'] = list(map(lambda tweet: get_created_at(tweet), unique_tweets))
    df['followers_count'] = list(map(lambda tweet: int(tweet['user']['followers_count']), unique_tweets))
    df['friends_count'] = list(map(lambda tweet: int(tweet['user']['friends_count']), unique_tweets))
    df['reply_id'] = list(map(lambda tweet: get_reply_id(tweet), unique_tweets))
    df['retweet_id'] = list(map(lambda tweet: get_retweet_id(tweet), unique_tweets))
    df['at_ids'] = list(map(lambda tweet: get_user_mentions(tweet), unique_tweets))
    df['text'] = list(map(lambda tweet: tweet['text'], unique_tweets))
    
    df = df[df.created_at >= dt.datetime.strptime(starttime, '%b %d %H:%M:%S %z %Y')]
    
    df = order_and_reindex(df, 'created_at')
    df['time_lapsed'] = 0
    first_tweet_datetime = df.created_at.iloc[0]
    for index in tqdm(range(len(df))):
        df.loc[index, 'time_lapsed'] = round((df.loc[index, 'created_at'] - first_tweet_datetime).total_seconds() / 60.0, 2)
    df = df[df.time_lapsed < float(timeframe)]
    
    return df


# In[6]:


if calculate_uniquetweets:
    unique_tweets = find_unique_tweets_crawled()
    print(unique_tweets.head())
    dump_tweets_dataframe(unique_tweets)

unique_tweets = load_tweets_dataframe()


# # Load Friends, and add new crawl relationships if necessary

# In[7]:


def merge_new_friends_dictionary():
    friends_dictionary = load_friends_dictionary()
    newcrawl_dictionary = load_newcrawl_dictionary()
    dump_friends_dictionary({**friends_dictionary, **newcrawl_dictionary})

if calculate_friends:
    merge_new_friends_dictionary()
    
friends_dictionary = load_friends_dictionary()


# # Unique Users

# In[8]:


def find_by_user_name(df, user_name):
    user = df[df.user == user_name]
    return user.iloc[0]

def find_by_user_id(df, user_id):
    user = df[df.user_id == user_id]
    return user.iloc[0]

def find_index_by_user_id(df, user_id):
    return df.user_id[df.user_id == user_id].index.tolist()[0]

def find_root_and_generation(df, index):
    row = df.iloc[index]
    time_lapsed = row.time_lapsed
    source_index = row.source_index
    generation = int(0)
    while source_index is not None:
        index = source_index
        row = df.iloc[index]
        source_index = row.source_index
        generation += 1
    root_time = row.time_lapsed
    return (index, generation, time_lapsed-root_time)

def find_unique_users():
    df = unique_tweets.copy()
    df = df.drop_duplicates(subset = ['user_id'])
    df = df.loc[:,['user', 'user_id', 'time_lapsed', 'followers_count', 'friends_count']]
    df['mention_and_reply'] = [[] for _ in range(len(df))]
    df['source_candidates'] = [[] for _ in range(len(df))]
    df['source_index'] = [None for _ in range(len(df))]
    df['seed_index'] = [None for _ in range(len(df))]
    df['generation'] = [None for _ in range(len(df))]
    df['time_since_seed'] = [None for _ in range(len(df))]
    
    df = order_and_reindex(df, 'time_lapsed')
    
    unique_user_id_set = set([int(x) for x in df.user_id])
    
    for index in tqdm(range(len(unique_tweets))):
        user_name = unique_tweets.loc[index, 'user']
        user_id = unique_tweets.loc[index, 'user_id']
        reply_id = unique_tweets.loc[index, 'reply_id']
        retweet_id = unique_tweets.loc[index, 'retweet_id']
        at_ids = unique_tweets.loc[index, 'at_ids']
        
        if reply_id is not None:
            if reply_id in unique_user_id_set:
                try:
                    find_by_user_id(df, user_id).mention_and_reply.append(find_index_by_user_id(df, int(reply_id)))
                except:
                    pass
        if retweet_id is not None:
            if retweet_id in unique_user_id_set:
                try:
                    find_by_user_id(df, user_id).mention_and_reply.append(find_index_by_user_id(df, int(retweet_id)))
                except:
                    pass
        for at_id in at_ids:
            if at_id in unique_user_id_set:
                try:
                    find_by_user_id(df, at_id).mention_and_reply.append(find_index_by_user_id(df, int(user_id)))
                except IndexError:
                    pass
            
    friends_not_found_list = []
    for index in tqdm(range(len(df))):
        user_id = str(df.loc[index, 'user_id'])
        try:
            friends = (set(friends_dictionary[int(user_id)]) & unique_user_id_set)
            friends_indexes = [find_index_by_user_id(df, x) for x in friends]
            friends_indexes.extend(df.loc[index, 'mention_and_reply'])
            friends_indexes = sorted([x for x in set(friends_indexes)])
            df.loc[index, 'source_candidates'].extend(friends_indexes)
            if len(friends_indexes) > 0:
                if (friends_indexes[0] < index):
                    df.loc[index, 'source_index'] = friends_indexes[0]
            df.loc[index, 'seed_index'], df.loc[index, 'generation'], df.loc[index, 'time_since_seed'] = find_root_and_generation(df, index)
        except KeyError:
            friends_not_found_list.append(index)
            
    print('Could not load friends for {}/{} entries'.format(len(friends_not_found_list), len(df)))
    return df


# In[9]:


if calculate_uniqueusers:
    unique_users = find_unique_users()
    print(unique_users.head())
    dump_users_dataframe(unique_users)
unique_users = load_users_dataframe()


# # Check Friends Dictionary

# In[10]:


def verify_friends_dictionary():
    friends_dictionary = load_friends_dictionary()
    crawled_set = set(friends_dictionary.keys())
    users_set = set(unique_users.user_id)
    need_to_crawl = users_set - crawled_set
    dump_needcrawl_set(need_to_crawl)
    print('Number of users still need to crawl: {}'.format(len(need_to_crawl)))   
    
    unwanted = set(crawled_set) - set(users_set)
    for unwanted_key in unwanted:
        del friends_dictionary[unwanted_key]
    dump_friends_dictionary(friends_dictionary)


# In[11]:


verify_friends_dictionary()
friends_dictionary = load_friends_dictionary()


# # Network

# In[12]:


# nx.write_gexf(network, 'givenchy_network.gexf')


# In[13]:


network_all = nx.DiGraph()
for index in tqdm(range(len(unique_users))):
    network_all.add_node(index,
                         user = unique_users.loc[index, 'user'],
                         user_id = unique_users.loc[index, 'user_id'],
                         time_lapsed = unique_users.loc[index, 'time_lapsed'],
                         followers_count = unique_users.loc[index, 'followers_count'],
                         friends_count = unique_users.loc[index, 'friends_count'],
                         generation = unique_users.loc[index, 'generation'],
                         time_since_seed = unique_users.loc[index, 'time_since_seed'],
                        )
    
    
    source_index = unique_users.loc[index, 'source_index']
    if source_index is not None:
        network_all.add_edge(source_index, index)

dump_networkx_all(network_all)


# In[14]:


unique_users.iloc[6].source_candidates


# In[15]:


network_friends = nx.DiGraph()
for index in tqdm(range(len(unique_users))):
    network_friends.add_node(index,
                             user = unique_users.loc[index, 'user'],
                             user_id = unique_users.loc[index, 'user_id'],
                             time_lapsed = unique_users.loc[index, 'time_lapsed'],
                             followers_count = unique_users.loc[index, 'followers_count'],
                             friends_count = unique_users.loc[index, 'friends_count'],
                             generation = unique_users.loc[index, 'generation'],
                             time_since_seed = unique_users.loc[index, 'time_since_seed'],
                            )
    source_candidates = unique_users.iloc[index].source_candidates
    for source_index in source_candidates:
        network_friends.add_edge(source_index, index)
dump_networkx_friends(network_friends)


# In[16]:


network_potential = nx.DiGraph()
for index in tqdm(range(len(unique_users))):
    network_potential.add_node(index,
                             user = unique_users.loc[index, 'user'],
                             user_id = unique_users.loc[index, 'user_id'],
                             time_lapsed = unique_users.loc[index, 'time_lapsed'],
                             followers_count = unique_users.loc[index, 'followers_count'],
                             friends_count = unique_users.loc[index, 'friends_count'],
                             generation = unique_users.loc[index, 'generation'],
                             time_since_seed = unique_users.loc[index, 'time_since_seed'],
                            )
    source_candidates = unique_users.iloc[index].source_candidates
    for source_index in source_candidates:
        if source_index < index:
            network_potential.add_edge(source_index, index)
dump_networkx_potential(network_potential)


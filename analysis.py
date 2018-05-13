
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

# Plots
import seaborn as sns
sns.set(color_codes=True)
import matplotlib.pylab as plt
plt.rcParams['figure.figsize'] = [15, 9]

import config
from config import load_us_city_state_files
city_to_state_dict, abbrev_to_state_dict, state_to_state_dict = load_us_city_state_files()

from config import load_friends_dictionary
friends_dictionary = load_friends_dictionary()


# In[2]:


calculate_uniquetweets = config.settings['calculate']['uniquetweets']
calculate_uniqueusers = config.settings['calculate']['uniqueusers']
calculate_network = config.settings['calculate']['network']
calculate_analysis = config.settings['calculate']['analysis']

file_input_path = config.settings['path']['twitter']
dates = config.settings['data']['dates']
search_phrases = config.settings['data']['phrases']
timeframe = config.settings['timeframe']
project_name = config.settings['data']['eventname']
starttime = config.settings['data']['starttime']


# In[3]:


def order_and_reindex(df, column):
    df = df.sort_values(by=[column])
    df = df.set_index(np.arange(len(df.index)))
    return df


# ## Unique Tweets

# In[4]:


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
    df['time'] = 0
    first_tweet_datetime = df.created_at.iloc[0]
    for index in tqdm(range(len(df))):
        df.loc[index, 'time'] = round((df.loc[index, 'created_at'] - first_tweet_datetime).total_seconds() / 60.0, 2)
    df = df[df.time < float(timeframe)]
    
    return df


# In[5]:


if calculate_uniquetweets:
    unique_tweets = find_unique_tweets_crawled()
    print(unique_tweets.head())
    with open(config.settings['path']['pickle']['tweets_dataframe'], 'wb') as tweets_dataframe_file:
        pickle.dump(unique_tweets, tweets_dataframe_file)


# In[6]:


with open(config.settings['path']['pickle']['tweets_dataframe'], 'rb') as tweets_dataframe_file:
        unique_tweets = pickle.load(tweets_dataframe_file)
        pprint('Loaded {} entries'.format(len(unique_tweets)))


# # Unique Users

# In[7]:


def find_by_user_name(df, user_name):
    user = df[df.user == user_name]
    return user.iloc[0]

def find_by_user_id(df, user_id):
    user = df[df.user_id == user_id]
    return user.iloc[0]

def find_unique_users():
    df = unique_tweets.copy()
    df = df.drop_duplicates(subset = ['user_id'])
    df = df.loc[:,['user', 'user_id', 'time', 'followers_count', 'friends_count']]
    df['source_candidates'] = [set([]) for _ in range(len(df))]
    df = order_and_reindex(df, 'time')
    
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
                    find_by_user_id(df, user_id).source_candidates.add(int(reply_id))
                except:
                    pass
        if retweet_id is not None:
            if retweet_id in unique_user_id_set:
                try:
                    find_by_user_id(df, user_id).source_candidates.add(int(retweet_id))
                except:
                    pass
        for at_id in at_ids:
            if at_id in unique_user_id_set:
                try:
                    find_by_user_id(df, at_id).source_candidates.add(int(user_id))
                except IndexError:
                    pass
            
    friends_not_found_list = []
    for index in tqdm(range(len(df))):
        user_id = str(df.loc[index, 'user_id'])
        try:
            friends = set(friends_dictionary[user_id]) & unique_user_id_set
            df.loc[index, 'source_candidates'].update(friends)
        except KeyError:
            friends_not_found_list.append(index)
    print('Could not load friends for {}/{} entries'.format(len(friends_not_found_list), len(df)))
    return df


# In[8]:


if calculate_uniqueusers:
    unique_users = find_unique_users()
    print(unique_users.head())
    with open(config.settings['path']['pickle']['users_dataframe'], 'wb') as users_dataframe_file:
        pickle.dump(unique_users, users_dataframe_file)


# In[9]:


with open(config.settings['path']['pickle']['users_dataframe'], 'rb') as users_dataframe_file:
        unique_users = pickle.load(users_dataframe_file)
        pprint('Loaded {} entries'.format(len(unique_users)))


# # Calculate Network

# In[10]:


def find_source(df, index):
    time_created = df.loc[index, 'time']
    try:
        candidate = df[df.user_id.isin(df.loc[index, 'source_candidates'])].iloc[0]
    except IndexError:
        return np.NaN
    if time_created > candidate.time:
        return candidate.user_id
    else:
        return np.NaN
    
def find_root_and_generation(df, index):
    row = df.iloc[index]
    time = row.time
    source = row.source_id
    generation = int(0)
    while ~np.isnan(source):
        row = df[df.user_id == source].iloc[0]
        source = row.source_id
        generation += 1
    root_time = row.time
    return (row.user_id, generation, time-root_time)
    
    
def find_network():
    df = unique_users.copy()
    df['source_id'] = [np.NaN for _ in range(len(df))]
    for index in tqdm(reversed(range(len(df)))):
        df.loc[index, 'source_id'] = find_source(unique_users, index)
    df = df.loc[:, ['user', 'user_id', 'source_id', 'time', 'followers_count', 'friends_count']]
    
    df['seed_user_id'] = [np.NaN for _ in range(len(df))]
    df['generation'] = [np.NaN for _ in range(len(df))]
    df['time_since_seed'] = [np.NaN for _ in range(len(df))]
    for index in tqdm(range(len(df))):
        df.loc[index, 'seed_user_id'], df.loc[index, 'generation'], df.loc[index, 'time_since_seed']= find_root_and_generation(df, index)
    return df


# In[11]:


if calculate_network:
    network = find_network()
    network.head()
    with open(config.settings['path']['pickle']['network_dataframe'], 'wb') as network_dataframe_file:
        pickle.dump(network, network_dataframe_file)


# In[12]:


with open(config.settings['path']['pickle']['network_dataframe'], 'rb') as network_dataframe_file:
        network = pickle.load(network_dataframe_file)
        pprint('Loaded {} entries'.format(len(network)))


# # Analysis

# In[13]:


def plot_hist_spreading_graph(df):
    title = 'Number of new infected users during first 24 hours, for event {}'.format(project_name)
    n_bins = math.floor(float(timeframe)/10)
    sns.distplot(df['time'], kde=False, bins=n_bins)
    plt.title(title)
    plt.xlabel('time (minutes) [10 minutes per bar]')
    plt.ylabel('number of new infected users')
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[14]:


def plot_generation_vs_log_number_of_infected_users(df):
    title = 'Generation vs number of infected users (log 10), for event {}'.format(project_name)
#     n_bins = math.floor(float(timeframe)/10)
    sns.distplot(df['generation'], kde=False, hist_kws={'log':True})
    plt.title(title)
    plt.xlabel('generation')
    plt.ylabel('number of infected users (log 10)')
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()
    
    print(df.groupby('generation').count())


# In[15]:


def plot_log_spreading_graph(df):
    title = 'Total number of new infected users (log10) during first 24 hours, for event {}'.format(project_name)
    number_of_seeds = 10
    seed_count_series = df.seed_user_id.value_counts()
    pallttes = sns.cubehelix_palette(number_of_seeds + 1)

    draw_dataframe = df.copy()
    draw_dataframe = draw_dataframe.filter(items=['time'])
    draw_dataframe = draw_dataframe.reset_index()
    draw_dataframe['counter'] = np.log10(range(1, len(draw_dataframe) + 1))
    plt.plot(draw_dataframe['time'], draw_dataframe['counter'], marker='', color=pallttes[number_of_seeds], linewidth=1, alpha=0.9, label = 'all')

    for index in range(number_of_seeds):
        seed_user_id = seed_count_series.keys()[index]
        data_to_plot = df.copy()
        data_to_plot = data_to_plot[data_to_plot.seed_user_id == seed_user_id]['time']
        data_to_plot = data_to_plot.reset_index()
        data_to_plot['counter'] = np.log10(range(1, len(data_to_plot) + 1))
        plt.plot(data_to_plot['time'], data_to_plot['counter'], marker='', color=pallttes[number_of_seeds - index], linewidth=1, alpha=0.9, label='Seed {}'.format(index + 1))

    plt.title(title)
    plt.xlabel('time t (minutes)')
    plt.ylabel('total number of new infected users at t (log base 10)')
    plt.legend()
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[16]:


def plot_time_after_spreading_vs_log_10_number_of_newly_infected_user(df):
    title = 'time (minutes) since seed creation time vs newly infected user {}'.format(project_name)
    number_of_seeds = 10
    seed_count_series = df.seed_user_id.value_counts()
    pallttes = sns.cubehelix_palette(number_of_seeds)
    
    for index in range(number_of_seeds):
        seed_user_id = seed_count_series.keys()[index]
        data_to_plot = df.copy()
        data_to_plot = data_to_plot[data_to_plot.seed_user_id == seed_user_id]['time_since_seed']
        data_to_plot = data_to_plot.reset_index()
        data_to_plot['counter'] = np.log10(range(1, len(data_to_plot) + 1))
        plt.plot(data_to_plot['time_since_seed'], data_to_plot['counter'], marker='', color=pallttes[number_of_seeds - index - 1], linewidth=1, alpha=0.9, label='Seed {}'.format(index + 1))

    plt.title(title)
    plt.xlabel('time (minutes)')
    plt.ylabel('number of new infected users (log base 10)')
    plt.legend()
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[17]:


def plot_time_vs_number_of_seeds():
    title = 'Time vs Number of seeds, for event {}'.format(project_name)
    seed_count_series = network.seed_user_id.value_counts()
    seeds_dataframe = network[network.user_id.isin(seed_count_series.keys())].copy()
    seeds_dataframe = order_and_reindex(seeds_dataframe, 'time')
    n_bins = math.floor(float(timeframe)/10)
    sns.distplot(seeds_dataframe['time'], kde=False, bins=n_bins, hist_kws={'log':True})
    plt.title(title)
    plt.xlabel('time (minutes) [10 minutes per bar]')
    plt.ylabel('number of seeds')
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[18]:


def plot_time_vs_number_of_seeds():
    title = 'Number of descendants(log 10) vs Number of seeds(log 10), for event {}'.format(project_name)
    seed_count_series = network.seed_user_id.value_counts()
    seeds_dataframe = network[network.user_id.isin(seed_count_series.keys())].copy()
    seeds_dataframe = order_and_reindex(seeds_dataframe, 'time')
    seeds_dataframe['y'] = 0
    for index in range(len(seeds_dataframe)):
        userid = seeds_dataframe.loc[index, 'user_id']
        seeds_dataframe.loc[index, 'y'] = np.log10(seed_count_series.get(userid))
    
    n_bins = 20
    
    sns.distplot(seeds_dataframe['y'], kde=False, bins=n_bins, hist_kws={'log':True})
    
#     sns.distplot(seeds_dataframe['y'], kde=False, bins=n_bins)
    plt.title(title)
    plt.xlabel('number of descendants')
    plt.ylabel('number of seeds')
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[19]:


def plot_time_vs_log_seed_descedants():
    title = 'Time vs Number of descendants (Log base 10) for event {}'.format(project_name)
    seed_count_series = network.seed_user_id.value_counts()
    seeds_dataframe = network[network.user_id.isin(seed_count_series.keys())].copy()
    seeds_dataframe = order_and_reindex(seeds_dataframe, 'time')
    seeds_dataframe['y'] = 0
    for index in range(len(seeds_dataframe)):
        userid = seeds_dataframe.loc[index, 'user_id']
        seeds_dataframe.loc[index, 'y'] = np.log10(seed_count_series.get(userid))
    seeds_dataframe.head()

    # use the function regplot to make a scatterplot
    sns.regplot(x=seeds_dataframe["time"], y=seeds_dataframe['y'], fit_reg=False)
    plt.title(title)
    plt.xlabel('time (minutes)')
    plt.ylabel('number of descendants (log base 10)')
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[20]:


def plot_followers_vs_log_seed_descedants():
    title = 'Number of followers (Log base 10) vs Number of descendants (Log base 10) for event {}'.format(project_name)
    seed_count_series = network.seed_user_id.value_counts()
    seeds_dataframe = network[network.user_id.isin(seed_count_series.keys())].copy()
    seeds_dataframe = order_and_reindex(seeds_dataframe, 'time')
    seeds_dataframe['y'] = 0
    for index in range(len(seeds_dataframe)):
        userid = seeds_dataframe.loc[index, 'user_id']
        seeds_dataframe.loc[index, 'y'] = seed_count_series.get(userid)
    
    # use the function regplot to make a scatterplot
    sns.regplot(
        x=np.log10(seeds_dataframe["followers_count"]), 
        y=np.log10(seeds_dataframe['y']), 
        fit_reg=False)
    plt.title(title)
    plt.xlabel('number of followers (log base 10)')
    plt.ylabel('number of descendants (log base 10)')
    plt.savefig('{}/{}'.format(config.settings['path']['result'], title))
    plt.show()


# In[21]:


def get_details_of_top_10_seeds():
    seed_count_series = network.seed_user_id.value_counts()
    seeds_dataframe = network[network.user_id.isin(seed_count_series.keys())].copy()
    seeds_dataframe = order_and_reindex(seeds_dataframe, 'time')
    seeds_dataframe['number_of_descendants'] = 0
    for index in range(len(seeds_dataframe)):
        userid = seeds_dataframe.loc[index, 'user_id']
        seeds_dataframe.loc[index, 'number_of_descendants'] = seed_count_series.get(userid)
    seeds_dataframe = seeds_dataframe.sort_values(by='number_of_descendants', ascending=False)
    seeds_dataframe = seeds_dataframe.set_index(np.arange(len(seeds_dataframe.index)))
    seeds_dataframe = seeds_dataframe.loc[:10, ['user', 'time', 'followers_count', 'number_of_descendants']]
    print(seeds_dataframe.to_latex())


# In[22]:


if calculate_analysis:
    plt.rcParams['figure.figsize'] = [15, 9]
    plot_hist_spreading_graph(network)
    plot_generation_vs_log_number_of_infected_users(network)
    plot_log_spreading_graph(network)    
    plot_time_after_spreading_vs_log_10_number_of_newly_infected_user(network)
    plot_time_vs_number_of_seeds()
    plot_time_vs_number_of_seeds()
    plot_time_vs_log_seed_descedants()
    plot_followers_vs_log_seed_descedants()
    get_details_of_top_10_seeds()


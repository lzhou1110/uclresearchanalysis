
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('cd', '..')


# In[2]:


import builtins
# builtins.uclresearch_topic = 'GIVENCHY'
# builtins.uclresearch_topic = 'HAWKING'
builtins.uclresearch_topic = 'NYC'
# builtins.uclresearch_topic = 'FLORIDA'
from configuration import config


# In[3]:


import time
import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import os
import sys
import pickle
from tqdm import tqdm
import datetime
import pandas as pd
import threading
import time


# In[4]:


class TwitterApi(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret): 
        self.consumer_key = consumer_key 
        self.consumer_secret = consumer_secret 
        self.access_token = access_token
        self.access_secret = access_secret

    def loadapi(self):
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        return tweepy.API(
            auth, 
            wait_on_rate_limit=True, 
            wait_on_rate_limit_notify=True, 
            compression=True)


# In[5]:


def crawl_friendship(thread_name, api, user_id):
    follower_ids = []
    try:
        c = tweepy.Cursor(api.friends_ids, id = user_id)
        for page in c.pages():
            follower_ids.extend(page)
    except tweepy.TweepError as e:
        print('tweepy.TweepError', e, ' from: ', thread_name)
    except:
        e = sys.exc_info()[0]
        print("Error: {}, from: {}".format(e, thread_name))  
    return follower_ids


# In[6]:


def save_friendship(thread_name, friendship_dictionary):
    filename = 'newcrawl-{date:%Y-%m-%d %H:%M:%S}-{}.dat'.format(
        thread_name, 
        date=datetime.datetime.now())
    config.dump_newcrawl_dictionary(friendship_dictionary, filename)


# In[7]:


class crwalThread(threading.Thread):
    def __init__(self, thread_id, thread_name, api, user_ids):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.api = api
        self.user_ids = user_ids
    def run(self):
        print('{}: {}'.format(self.thread_name, ': starting'))
        dump_dictionary_if_over_this_size = 100
        friends_dictionary = {}
        while len(self.user_ids) > 0:
            user_id = self.user_ids.pop()
            friends_dictionary[user_id] = crawl_friendship(self.thread_name, self.api, user_id)
            if len(friends_dictionary.keys()) >= dump_dictionary_if_over_this_size:
                save_friendship(self.thread_name, friends_dictionary)
                friends_dictionary = {}
        save_friendship(self.thread_name, friends_dictionary)
        print('{}: {}'.format(self.thread_name, ': exiting'))


# In[8]:


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


# In[9]:


keys = config.load_twitter_keys()
number_of_apis = len(keys.index)
print('Found {} apis, could crawl {} friendships per day'.format(keys.shape[0], keys.shape[0] * 60 * 24))
need_to_crawl = list(config.load_needcrawl_set())
print('Number of users we still need to crawl: {}'.format(len(need_to_crawl)))
splitted_user_ids = list(split(need_to_crawl, keys.shape[0]))

threads = []
for index, row in keys.iterrows():    
    twitterApi = TwitterApi(row.consumer_key, row.consumer_secret, row.access_token, row.access_secret).loadapi()
    threads.append(crwalThread(index, row.reference, twitterApi, splitted_user_ids[0]))

for each_thread in threads:
    each_thread.start()    
    
for each_thread in threads:
    each_thread.join()
    
print("Finished crawling")



# coding: utf-8

# In[1]:


import time
import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import os
import sys
import pickle
from tqdm import tqdm


# In[2]:


import config
from config import load_users_dataframe
users_dataframe = load_users_dataframe()


# In[3]:


print(users_dataframe.head())


# In[4]:


from config import load_friends_dictionary
from config import save_friends_dictionary


# In[5]:


class TwitterApi(object):
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret): 
        self.consumer_key = consumer_key 
        self.consumer_secret = consumer_secret 
        self.access_token = access_token
        self.access_secret = access_secret

    def loadapi(self):
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_secret)
        return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

twitter_api_list = []
# Jimmy Canteen 0
twitter_api_list.append(TwitterApi(
    'ogd44qNt9NHukPsUsnKmn1Wm3', 
    'g0PMron4C0eOD7NYpSqekzUwPwRafUpYTOKgiAabA5fkpS2a4l', 
    '936587907007176704-2xAvOIe5u5FTkuAanmWLJRkwKlMPqnD',
    'DTJQl1JjQdbVErGlTGBI7g7wyHeWt8o0eQZJIb4fewn3J'
).loadapi())
# BarberDdddavid 1
twitter_api_list.append(TwitterApi(
    'Imk26gt1YacAmZqsBvwXNNZp1', 
    'ZTVGMr0B6e8PLaFWFtQFbBSta4e0E3POjZO0Ps4uU7XX2jp08c', 
    '948501581372280832-2Ux6iejRB0Mr7KOyQ2psV5hgN8rCvAW',
    'cwCusThG5QGtLoLusElVWdMKtZ8VHvJmngBGjqCkpO77S'
).loadapi())
# Hu13Steve 2
twitter_api_list.append(TwitterApi(
    'Lqz4r2UGJ3MALpX7TygEWkdvu', 
    '4irrPlKdKpqdo35PAlqx1g7oTLXL79KGh8ul0Ug3NP7NPnJ5fq', 
    '948494955756052481-HBHi8eC43VnafcgKj1hfQrkiQgdazld',
    '1hfPh52QxAWtku4AqNnjUytGCWyt4AkNllR0RGdNag5wW'
).loadapi())
# james13_david 3
twitter_api_list.append(TwitterApi(
    'QweR1meYNPziTVMQfnPBw7u7L', 
    'w2imXsR0TKSqafgZP0LU1spudls7SnCcUqskUUubmvmstbah5S', 
    '940722476585312257-i94glXYrPQa4LYqhLz75qNfaDHXrFpU',
    'xezy1i3SKqkiVVBHy25avg1pybkfuR1CIbUzRGj5mq6Mo'
).loadapi())
# hui's crawler 4
twitter_api_list.append(TwitterApi(
    'FImHy1gMljimQMQxG6432rATE', 
    '8oNc5WX3srEophN8oiGrnBeta1iX1QWPM9IDl3scyuzitHZkTp', 
    '1976839820-bH0EOOIuJQC5yqZRDv5iJo8Gpp3Uerz76OOug99',
    'ntdfl0pjZZYVHsLTDK1wKiEsKHS5B9mAdvyCDhREQqDzG'
).loadapi())
# lzhoudevuk 5 
twitter_api_list.append(TwitterApi(
    'MP1ydHbs9wSPCvUO0HcJlBd1s', 
    'yeVQtGsq4pgYrX6tBqMtKcscrGULJE9SCPyP38vFDaAhUtSJiw', 
    '959980110588899329-A943y5m9XFhivFJXXw0N1uRSdesdYlY',
    'hP63SwoueduNQSSe4pwlZNhegjJCXVn4qjeZPfv762KsJ'
).loadapi())
# lzhoudevcn 6 
twitter_api_list.append(TwitterApi(
    'cM2Ket4JdIrFCoFJfZR6dKEJW', 
    'VzewbPMeZcIu8aakQ0cnOmhPnJmHhazFDG9cCSgka01JqT463a', 
    '959978501125402624-iRPiJiSVy7TDihEf1HsV74Ow72iavWO',
    'ZvInw0gQb8xRvMLwoG6PDy18JwM66vhhyFnskeisZBGRe'
).loadapi())
# lzhoudevau passed 7 
twitter_api_list.append(TwitterApi(
    'pbFZlAThsyleV4IWazYaG6WH0', 
    'w01obwo4ECZfl4aIbhEA8q5GnMGTKVXiWvsDq6D8eE4DiwTpps', 
    '959974918619385856-sGUbwHJQd8YrdoNkJGDTyvpafFjh7wi',
    '676MhvwxiPZoUv6f8Upm2fVaZiPUa5jDvCwFHA05HowiE'
).loadapi())
# ucablz4 passed 8
twitter_api_list.append(TwitterApi(
    'CeIvDs3UbPO4Yj4XK6ZFHzVIU', 
    'j0eRROwvGFk1CEciSehtUOc2SCVmxzMhWbQd3sUDhztdICPtMW', 
    '930982504596672517-AE7R6i4xaNPUeXME2S4cyeTgSJNBVEv',
    'JEmF4hPSTD65lFmYM1Zm3x4I6Xf7kUQ93NvlodJ2jPrQN'
).loadapi())
# liyi.zhou.17 passed 9
twitter_api_list.append(TwitterApi(
    'AdCVM7NUpICq9RcYnZiM68FLb', 
    '0hbBfyXK8CBCvl9S6Zu1CkWTlAo1c4rvfsAl8ot4VPehTLpHL4', 
    '930982019672178689-UpCYlSLDFDiwcr44weBZoDO4CY2npyE',
    's3Z5H1cADAMYElfGhYCE27ZQSWNR4EP2n1FcJmcwG80ZB'
).loadapi())
# lzhou1110 10
twitter_api_list.append(TwitterApi(
    'yom0HoCImxDZobnZzDrJsESke',
    'iPDqeGyq40FbovpFUoLdunLnFINEDB5MQuzFFbo0KBoBiM4mk0',
    '910787059501150208-vvOcHytvhGncJTtuAF23tywLu5UTSbL',
    'lL4vIlZlKMurhhgsZGM11hGh6LG6cUBtaHqbMiLYJTZhj'
).loadapi())
# tao 11
twitter_api_list.append(TwitterApi(
    'YZD91p9NpWydELrliHkx3FkV2',
    'dchHYkpVxp7Uq1Mi5fA94GfCKWFUrQ1VRp0kQJsI2nXXTJjqUk',
    '960929372206223360-TgkpvCQWqTdf9Po9DaOJCrOCGHiMGVV',
    'pRCYaoy3cKWmzvIZ3rDExlxSBI1SVTVIGLRfvpzFxTaVp'
).loadapi())
# wu api 12
twitter_api_list.append(TwitterApi(
    '6hDKNKAEVflvc1QiKWRwEvqIU',
    'LAOoZL1qKs4l9VTyWRKOibLj4tm14n6ZziMX9wd9Wo3NJ8ADyC',
    '961193810951856129-nGfaxWcrgS4i0gReDmyg68xOZoWiBPU',
    'xDwZpIXjrvcUZpqxz39e77XM924Ek9tBQ69aC9JtDPMEC'
).loadapi())
# peter.liyi.z api 13
twitter_api_list.append(TwitterApi(
    'AFRdbq1jpYv5uHzc2XXilJBMY',
    'UvSj6ZnbUG0t3nQASgd7kSHeiCoL14Iadt4f8gI4Y4QhsanovG',
    '2166615014-QcdbmCt252E02I2wAMVgXAJMXtE5tgyQpABuAkr',
    '5nYYyhO1WenLXLuuQ6Kthlg8xOg7wlcX7zEP1aLg6abHT'
).loadapi())
# miao api 14
twitter_api_list.append(TwitterApi(
    'FlmshcUW970JhOuWCrffznTzM',
    '33oh92E47FaeQm6GNWvC5axvmN3nRm6IKhKwN7UX7Xys7pfCtA',
    '320714154-woEAipLwLvVwkJo2o9i5IYvoSaFGqzV6pN8nTboL',
    'M0UVpBAPdGI3yzfXqXd7vhcx4DRttCLV9LsQTjRR7Fpei'
).loadapi())
# ucl lzhou adlrl account 15
twitter_api_list.append(TwitterApi(
    '45mvtiqyyq5B1cXi6kPJHq2TO',
    'yrCn2qyWiyYNZXgGX0RhHCAUFV0pjg30twa9txtwltX2CYJvRy',
    '961358756595535873-obN8fa0WJRG7y5ptgtEbO0btCXWagwx',
    'hCKeIKCThs1xmCUsiaMms0jkHXNshVHSVTu1hbUcTa1kz'
).loadapi())
# ucl lzhou adlrl account ucablz4 16
twitter_api_list.append(TwitterApi(
    '75xtkzO360GjmMgLhaSZ1zH0u',
    '2QM0T8J3Jwy4aJEuaTJk9GT6PxkcFVpGqgwoqWvmkvgvq7mqdr',
    '961359707809157122-EUhutRfRHEBPSeE791pVGzYd2oMMq87',
    'WrgrnvyxVNBFNtkDwD4e1sGw2rQNhvbiOU9YaGkgcK1jA'
).loadapi())


# In[6]:


def tweet_find_friends(api, user_id, logger):
    follower_ids = []
    try:
        c = tweepy.Cursor(api.friends_ids, id = user_id)
        for page in c.pages():
            follower_ids.extend(page)
    except tweepy.TweepError as e:
        print('tweepy.TweepError', e, ' from: ', logger)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)  
    return follower_ids
        
def crawl_twitter_friend(api, friends_dictionary, user_id, logger):
    friends_dictionary[user_id] = tweet_find_friends(api, user_id, logger)
    
# def find_friends(api, friends_dictionary, user_id, logger):
#     if user_id not in friends_dictionary.keys():
#         friends_dictionary[user_id] = tweet_find_friends(api, user_id, logger)
#         save_friends_dictionary(friends_dictionary)
#         load_friends_dictionary()
#         return friends_dictionary[user_id], 1
#     return friends_dictionary[user_id], 0

# def find_first_intersection_element(listA, listB):
#     for element in listA:
#         if element in listB:
#             return element
#     return ''


# In[7]:


friends_dictionary = load_friends_dictionary()
all_users = set(users_dataframe.user_id)
found_users = set(friends_dictionary.keys())
need_to_crawl = all_users - found_users
print('Number of users we still need to crawl: {}'.format(len(need_to_crawl)))


# In[ ]:


api_counter = 0
number_of_apis = len(twitter_api_list)
with tqdm(total = len(need_to_crawl), unit='Twitter friendship', unit_scale=True, unit_divisor=1024) as pbar:
    while len(need_to_crawl) != 0:
        for api_counter in range(min(len(need_to_crawl), number_of_apis)):
            user_id = need_to_crawl.pop()
            crawl_twitter_friend(twitter_api_list[api_counter], friends_dictionary, user_id, api_counter)
        pbar.update(number_of_apis)
        save_friends_dictionary(friends_dictionary)
        friends_dictionary = load_friends_dictionary()


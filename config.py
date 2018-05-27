import os
import configparser
import pickle
from pprint import pprint

root_path = os.getcwd()

config = configparser.RawConfigParser()
config.read('env.properties')
config.read('env_parameters.properties')

BASE = 'BASE'
profile = config.get(BASE, 'profile')

settings = {}
settings['timeframe'] = config.get(BASE, 'timeframe')
settings['calculate'] = {}
settings['calculate']['uniquetweets'] = config.get(BASE, 'calculate.uniquetweets') == 'True'
settings['calculate']['uniqueusers'] = config.get(BASE, 'calculate.uniqueusers') == 'True'
settings['calculate']['network'] = config.get(BASE, 'calculate.network') == 'True'
settings['calculate']['analysis'] = config.get(BASE, 'calculate.analysis') == 'True'
settings['calculate']['friends'] = config.get(BASE, 'calculate.friends') == 'True'

settings['path'] = {}
settings['path']['cwd'] = root_path + config.get(profile, 'path.project')
settings['path']['newcrawl'] = root_path + config.get(BASE, 'path.newcrawl')
settings['path']['twitter'] = settings['path']['cwd'] + config.get(BASE, 'path.twitter')
settings['path']['result'] = settings['path']['cwd'] + config.get(BASE, 'path.result')

pickle_path = settings['path']['cwd'] + config.get(BASE, 'path.pickle')
settings['path']['pickle'] = {}
settings['path']['pickle']['tweets'] = pickle_path+ config.get(BASE, 'path.pickle.tweets')
settings['path']['pickle']['users'] = pickle_path+ config.get(BASE, 'path.pickle.users')
settings['path']['pickle']['network'] = pickle_path+ config.get(BASE, 'path.pickle.network')
settings['path']['pickle']['friends'] = pickle_path + config.get(BASE, 'path.pickle.friends')
settings['path']['pickle']['needcrawl'] = pickle_path + config.get(BASE, 'path.pickle.needcrawl')


settings['data'] = {}
settings['data']['starttime'] = config.get(profile, 'data.starttime')
settings['data']['eventname'] = config.get(profile, 'data.eventname')
settings['data']['dates'] = config.get(profile, 'data.dates').split(',')
settings['data']['phrases'] = config.get(profile, 'data.phrases').split(',')
pprint(settings)


def load_pickle_file(path):
    print('Loading data file from path {}'.format(path))
    try:
        with open(path, 'rb') as file:
            data = pickle.load(file)
            pprint('Loaded {} entires'.format(len(data)))
            return data
    except Exception as e: raise
    
def save_pickle_file(path, data):
    print('Dumping data to path {}'.format(path))
    with open(path, 'wb') as file:
        pickle.dump(data, file)
    pprint('Finished dumping data to path {}'.format(path))
    

def load_tweets_dataframe():
    return load_pickle_file(settings['path']['pickle']['tweets'])

def dump_tweets_dataframe(data):
    save_pickle_file(settings['path']['pickle']['tweets'], data)

def load_users_dataframe():
    return load_pickle_file(settings['path']['pickle']['users'])

def dump_users_dataframe(data):
    save_pickle_file(settings['path']['pickle']['users'], data)
    
def load_network_dataframe():
    return load_pickle_file(settings['path']['pickle']['network'])

def dump_network_dataframe(data):
    save_pickle_file(settings['path']['pickle']['network'], data)
    
def load_friends_dictionary():
    return load_pickle_file(settings['path']['pickle']['friends'])

def dump_friends_dictionary(data):
    save_pickle_file(settings['path']['pickle']['friends'], data)
    
def load_needcrawl_set():
    return load_pickle_file(settings['path']['pickle']['needcrawl'])
    
def dump_needcrawl_set(data):
    save_pickle_file(settings['path']['pickle']['needcrawl'], data)
    
def load_newcrawl_dictionary():
    return load_pickle_file(settings['path']['newcrawl'])
    
def dump_newcrawl_dictionary(data):
    save_pickle_file(settings['path']['newcrawl'], data)
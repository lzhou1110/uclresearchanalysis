import os
import configparser
import pickle
from pprint import pprint

BASE = 'BASE'

config = configparser.RawConfigParser()
config.read('configfile.properties')
profile = config.get(BASE, 'profile')

settings = {}
root_path = os.getcwd()
settings['timeframe'] = config.get(BASE, 'timeframe') 
settings['path'] = {}
settings['path']['cwd'] = root_path + config.get(profile, 'path.project') 
settings['path']['twitter'] = settings['path']['cwd'] + config.get(profile, 'path.twitter')
settings['path']['result'] = settings['path']['cwd'] + config.get(profile, 'path.result')
settings['path']['friends_dictionary'] = root_path + config.get(BASE, 'path.friends_dictionary')
pickle_path = settings['path']['cwd'] + config.get(profile, 'path.pickle')
settings['path']['pickle'] = {}
settings['path']['pickle']['tweets_dataframe'] = pickle_path+ config.get(profile, 'path.pickle.tweets_dataframe')
settings['path']['pickle']['users_dataframe'] = pickle_path+ config.get(profile, 'path.pickle.users_dataframe')
settings['path']['pickle']['network_dataframe'] = pickle_path+ config.get(profile, 'path.pickle.network_dataframe')
settings['data'] = {}
settings['data']['eventname'] = config.get(profile, 'data.eventname')
settings['data']['dates'] = config.get(profile, 'data.dates').split(',')
settings['data']['phrases'] = config.get(profile, 'data.phrases').split(',')
pprint(settings)

def load_us_city_state_files():
    pprint('Load city and state dictionaries from dat files')
    with open('other/us_city_state/city_to_state_dict.dat', 'rb') as city_to_state_dict_file:
        city_to_state_dict = pickle.load(city_to_state_dict_file)
    with open('other/us_city_state/abbrev_to_state_dict.dat', 'rb') as abbrev_to_state_dict_file:
        abbrev_to_state_dict = pickle.load(abbrev_to_state_dict_file)
    with open('other/us_city_state/state_to_state_dict.dat', 'rb') as state_to_state_dict_file:
        state_to_state_dict = pickle.load(state_to_state_dict_file)
    pprint('loaded {} states abbrev, loaded {} states, loaded {} cities'.format(
        len(abbrev_to_state_dict), 
        len(state_to_state_dict), 
        len(city_to_state_dict)))
    return city_to_state_dict, abbrev_to_state_dict, state_to_state_dict

def load_friends_dictionary():
    with open(settings['path']['friends_dictionary'], 'rb') as friends_dictionary_file:
        friends_dictionary = pickle.load(friends_dictionary_file)
        pprint('Loaded {} friends dictionary'.format(len(friends_dictionary)))
        return friends_dictionary

def save_friends_dictionary(friends_dictionary): 
    with open(settings['path']['friends_dictionary'], 'wb') as friends_dictionary_file:
        pickle.dump(friends_dictionary, friends_dictionary_file)     

def load_users_dataframe():
    pprint('Loading users dataframe')
    with open(settings['path']['pickle']['users_dataframe'], 'rb') as users_file:
        users_dataframe = pickle.load(users_file)
        pprint('Loaded {} entries'.format(len(users_dataframe)))
        return users_dataframe
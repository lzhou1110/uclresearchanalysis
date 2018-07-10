
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('cd', '..')


# In[2]:


import builtins
builtins.uclresearch_topic = 'GIVENCHY' # 226984 entires
# builtins.uclresearch_topic = 'HAWKING' # 4828104 entries
# builtins.uclresearch_topic = 'NYC'
# builtins.uclresearch_topic = 'FLORIDA'
from configuration import config


# In[3]:


import networkx as nx
from tqdm import tqdm
import pandas as pd
import numpy as np
import math
import multiprocessing
from multiprocessing import Pool
from IPython.display import display


# In[4]:


unique_users = config.load_users_dataframe()
network_friends = config.load_networkx_friends()


# In[5]:


unique_users.columns


# # Settings

# In[6]:


# intervals = [60, 30, 15, 7]
intervals = [30]

# Helper function for mean value calculation
def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


# # Pre-Calculate features

# In[7]:


get_ipython().run_cell_magic('time', '', '# Calculating in and out degrees\nnodeInDegreeDict = network_friends.in_degree()\nnodeOutDegreeDict = network_friends.out_degree()')


# In[8]:


get_ipython().run_cell_magic('time', '', 'convert_dictionary_to_sorted_list = lambda x: [x[a] for a in sorted(x)]')


# Assortativity [https://networkx.github.io/documentation/networkx-1.9.1/reference/algorithms.assortativity.html]

# In[9]:


get_ipython().run_cell_magic('time', '', 'average_neighbor_degree = convert_dictionary_to_sorted_list(nx.average_neighbor_degree(network_friends))')


# Centrality [https://networkx.github.io/documentation/networkx-1.9.1/reference/algorithms.centrality.html]

# In[10]:


get_ipython().run_cell_magic('time', '', 'degree_centrality = convert_dictionary_to_sorted_list(nx.degree_centrality(network_friends))')


# In[11]:


get_ipython().run_cell_magic('time', '', 'in_degree_centrality = convert_dictionary_to_sorted_list(nx.in_degree_centrality(network_friends))')


# In[12]:


get_ipython().run_cell_magic('time', '', 'out_degree_centrality = convert_dictionary_to_sorted_list(nx.out_degree_centrality(network_friends))')


# In[13]:


# Too slow
# %%time
# closeness_centrality = convert_dictionary_to_sorted_list(nx.closeness_centrality(network_friends))


# In[14]:


# Too slow
# %%time
# betweenness_centrality = convert_dictionary_to_sorted_list(nx.betweenness_centrality(network_friends))


# In[15]:


get_ipython().run_cell_magic('time', '', 'eigenvector_centrality = convert_dictionary_to_sorted_list(nx.eigenvector_centrality(network_friends))')


# # Feature Extraction

# In[16]:


def process_data(interval, start_index, end_index):
    features = {
        'label': [],
        'user_index': [],
        # UsM: User metadata
        'UsM_deltaDays': [],
        'UsM_statusesCount': [],
        'UsM_followersCount': [],
        'UsM_favouritesCount': [],
        'UsM_friendsCount': [],
        'UsM_listedCount': [],
        'UsM_normalizedUserStatusesCount': [],
        'UsM_normalizedUserFollowersCount': [],
        'UsM_normalizedUserFavouritesCount': [],
        'UsM_normalizedUserListedCount': [],
        'UsM_normalizedUserFriendsCount': [],                 
        'UsM_deltaDays0': [],
        'UsM_statusesCount0': [],
        'UsM_followersCount0': [],
        'UsM_favouritesCount0': [],
        'UsM_friendsCount0': [],
        'UsM_listedCount0': [],
        'UsM_normalizedUserStatusesCount0': [],
        'UsM_normalizedUserFollowersCount0': [],
        'UsM_normalizedUserFavouritesCount0': [],
        'UsM_normalizedUserListedCount0': [],
        'UsM_normalizedUserFriendsCount0': [],
        'UsM_deltaDays-1': [],
        'UsM_statusesCount-1': [],
        'UsM_followersCount-1': [],
        'UsM_favouritesCount-1': [],
        'UsM_friendsCount-1': [],
        'UsM_listedCount-1': [],
        'UsM_normalizedUserStatusesCount-1': [],
        'UsM_normalizedUserFollowersCount-1': [],
        'UsM_normalizedUserFavouritesCount-1': [],
        'UsM_normalizedUserListedCount-1': [],
        'UsM_normalizedUserFriendsCount-1': [],
        # TwM: Tweet metadata
        'TwM_t0': [],
        'TwM_t-1': [],
        'TwM_tCurrent': [],
        # Nw: Network
        'Nw_nNodes': [],
        'Nw_averageNeighborDegree': [],
        'Nw_degreeCentrality': [],
        'Nw_inDegreeCentrality': [],
        'Nw_outDegreeCentrality': [],
        'Nw_eigenvectorCentrality': [],
        'Nw_averageNeighborDegree0': [],
        'Nw_degreeCentrality0': [],
        'Nw_inDegreeCentrality0': [],
        'Nw_outDegreeCentrality0': [],
        'Nw_eigenvectorCentrality0': [],
        'Nw_averageNeighborDegree-1': [],
        'Nw_degreeCentrality-1': [],
        'Nw_inDegreeCentrality-1': [],
        'Nw_outDegreeCentrality-1': [],
        'Nw_eigenvectorCentrality-1': [],
        # Stat: Statistical
        'Stat_average_kOut': [],
        'Stat_average_t': [],
        'Stat_average_deltaDays': [],
        'Stat_average_statusesCount': [],
        'Stat_average_followersCount': [],
        'Stat_average_favouritesCount': [],
        'Stat_average_friendsCount': [],
        'Stat_average_listedCount': [],
        'Stat_average_normalizedUserStatusesCount': [],
        'Stat_average_normalizedUserFollowersCount': [],
        'Stat_average_normalizedUserFavouritesCount': [],
        'Stat_average_normalizedUserListedCount': [],
        'Stat_average_normalizedUserFriendsCount': [],                
        'Stat_max_kOut': [],
        'Stat_min_kOut': []
    }

    with tqdm(total=len(list(unique_users[start_index: end_index].iterrows()))) as pbar: 
        for index, user_row in unique_users[start_index: end_index].iterrows():
            if user_row['source_index'] is not None:          
                source_candidates = user_row['source_candidates']
                source_first = source_candidates[0]
                source_first_row = unique_users.iloc[source_first]
                source_first_time_lapsed = source_first_row.time_lapsed
                start_bar = int(source_first_time_lapsed / interval) + 1                
                bars = list(np.arange(start_bar * interval, 24 * 60, interval))
                number_of_bars = len(bars)
                
                for current_time in bars:
                    # all sources up to the current time
                    sources = [x for x in source_candidates if unique_users.iloc[x].time_lapsed <= current_time]
                    sources_dataframe = unique_users.iloc[sources]
                    
                    averageNeighborDegreeList = list(average_neighbor_degree[i] for i in sources)
                    degreeCentralityList = list(degree_centrality[i] for i in sources)
                    inDegreeCentralityList = list(in_degree_centrality[i] for i in sources)
                    outDegreeCentralityList = list(out_degree_centrality[i] for i in sources)
                    eigenvectorCentralityList = list(eigenvector_centrality[i] for i in sources)
                    
                    degreeList = [nodeOutDegreeDict[x] for x in sources]
                    timeList = [current_time - unique_users.iloc[x].time_lapsed for x in sources]
                    
                    first_source_index = sources[0]
                    first_source_row = unique_users.iloc[first_source_index]
                    last_source_index = sources[-1]
                    last_source_row = unique_users.iloc[last_source_index]

                    #Extraction
                    features['label'].append(int(current_time >= user_row['time_lapsed']))
                    features['user_index'].append(index)
                    # UsM: User metadata                    
                    features['UsM_deltaDays'].append(user_row['user_created_days'])
                    features['UsM_statusesCount'].append(user_row['user_statuses_count'])
                    features['UsM_followersCount'].append(user_row['followers_count'])
                    features['UsM_favouritesCount'].append(user_row['user_favourites_count'])
                    features['UsM_friendsCount'].append(user_row['friends_count'])
                    features['UsM_listedCount'].append(user_row['user_listed_count'])
                    features['UsM_normalizedUserStatusesCount'].append(user_row['normalized_user_statuses_count'])
                    features['UsM_normalizedUserFollowersCount'].append(user_row['normalized_user_followers_count'])
                    features['UsM_normalizedUserFavouritesCount'].append(user_row['normalized_user_favourites_count'])
                    features['UsM_normalizedUserListedCount'].append(user_row['normalized_user_listed_count'])
                    features['UsM_normalizedUserFriendsCount'].append(user_row['normalized_user_friends_count'])                 
                    features['UsM_deltaDays0'].append(source_first_row.user_created_days)
                    features['UsM_statusesCount0'].append(source_first_row.user_statuses_count)
                    features['UsM_followersCount0'].append(source_first_row.followers_count)
                    features['UsM_favouritesCount0'].append(source_first_row.user_favourites_count)
                    features['UsM_friendsCount0'].append(source_first_row.friends_count)
                    features['UsM_listedCount0'].append(source_first_row.user_listed_count)
                    features['UsM_normalizedUserStatusesCount0'].append(source_first_row.normalized_user_statuses_count)
                    features['UsM_normalizedUserFollowersCount0'].append(source_first_row.normalized_user_followers_count)
                    features['UsM_normalizedUserFavouritesCount0'].append(source_first_row.normalized_user_favourites_count)
                    features['UsM_normalizedUserListedCount0'].append(source_first_row.normalized_user_listed_count)
                    features['UsM_normalizedUserFriendsCount0'].append(source_first_row.normalized_user_friends_count)
                    features['UsM_deltaDays-1'].append(last_source_row.user_created_days)
                    features['UsM_statusesCount-1'].append(last_source_row.user_statuses_count)
                    features['UsM_followersCount-1'].append(last_source_row.followers_count)
                    features['UsM_favouritesCount-1'].append(last_source_row.user_favourites_count)
                    features['UsM_friendsCount-1'].append(last_source_row.friends_count)
                    features['UsM_listedCount-1'].append(last_source_row.user_listed_count)
                    features['UsM_normalizedUserStatusesCount-1'].append(last_source_row.normalized_user_statuses_count)
                    features['UsM_normalizedUserFollowersCount-1'].append(last_source_row.normalized_user_followers_count)
                    features['UsM_normalizedUserFavouritesCount-1'].append(last_source_row.normalized_user_favourites_count)
                    features['UsM_normalizedUserListedCount-1'].append(last_source_row.normalized_user_listed_count)
                    features['UsM_normalizedUserFriendsCount-1'].append(last_source_row.normalized_user_friends_count) 
                    # TwM: Tweet metadata
                    features['TwM_t0'].append(round(timeList[0], 1))
                    features['TwM_t-1'].append(round(timeList[-1], 1))
                    features['TwM_tCurrent'].append(current_time)
                    # Nw: Network
                    features['Nw_nNodes'].append(len(sources))
                    features['Nw_averageNeighborDegree'].append(average_neighbor_degree[index])
                    features['Nw_degreeCentrality'].append(degree_centrality[index])
                    features['Nw_inDegreeCentrality'].append(in_degree_centrality[index])
                    features['Nw_outDegreeCentrality'].append(out_degree_centrality[index])
                    features['Nw_eigenvectorCentrality'].append(eigenvector_centrality[index])
                    features['Nw_averageNeighborDegree0'].append(average_neighbor_degree[source_first])
                    features['Nw_degreeCentrality0'].append(degree_centrality[source_first])
                    features['Nw_inDegreeCentrality0'].append(in_degree_centrality[source_first])
                    features['Nw_outDegreeCentrality0'].append(out_degree_centrality[source_first])
                    features['Nw_eigenvectorCentrality0'].append(eigenvector_centrality[source_first])
                    features['Nw_averageNeighborDegree-1'].append(average_neighbor_degree[last_source_index])
                    features['Nw_degreeCentrality-1'].append(degree_centrality[last_source_index])
                    features['Nw_inDegreeCentrality-1'].append(in_degree_centrality[last_source_index])
                    features['Nw_outDegreeCentrality-1'].append(out_degree_centrality[last_source_index])
                    features['Nw_eigenvectorCentrality-1'].append(eigenvector_centrality[last_source_index])
                    # Stat: Statistical
                    features['Stat_average_kOut'].append(round(mean(degreeList), 1))
                    features['Stat_average_t'].append(round(mean(timeList), 1))
                    features['Stat_average_deltaDays'].append(sources_dataframe.user_created_days.mean())
                    features['Stat_average_statusesCount'].append(sources_dataframe.user_statuses_count.mean())
                    features['Stat_average_followersCount'].append(sources_dataframe.followers_count.mean())
                    features['Stat_average_favouritesCount'].append(sources_dataframe.user_favourites_count.mean())
                    features['Stat_average_friendsCount'].append(sources_dataframe.friends_count.mean())
                    features['Stat_average_listedCount'].append(sources_dataframe.user_listed_count.mean())
                    features['Stat_average_normalizedUserStatusesCount'].append(sources_dataframe.normalized_user_statuses_count.mean())
                    features['Stat_average_normalizedUserFollowersCount'].append(sources_dataframe.normalized_user_followers_count.mean())
                    features['Stat_average_normalizedUserFavouritesCount'].append(sources_dataframe.normalized_user_favourites_count.mean())
                    features['Stat_average_normalizedUserListedCount'].append(sources_dataframe.normalized_user_listed_count.mean())
                    features['Stat_average_normalizedUserFriendsCount'].append(sources_dataframe.normalized_user_friends_count.mean())
                    features['Stat_max_kOut'].append(max(degreeList))
                    features['Stat_min_kOut'].append(min(degreeList))
                processed_dataframe = pd.DataFrame(features)
            pbar.update(1)
    return processed_dataframe


# In[17]:


number_of_processes = multiprocessing.cpu_count()
print('Will start {} processes'.format(number_of_processes))
for interval in intervals:
    with Pool(number_of_processes) as pool:
        parameters = []
        number_of_users = len(unique_users.index)
        task_size = math.ceil(number_of_users/number_of_processes)
        for i in range(number_of_processes):
            start_index = i * task_size
            end_index = min((i + 1) * task_size, number_of_users)
            parameters.append((interval, start_index, end_index))
        dataframe_results = pool.starmap(process_data, parameters)
    result = pd.DataFrame()
    result = result.append(dataframe_results)
    config.dump_ml_data(result, interval)
    print('extracted {} of rows'.format(len(result.index)))
    display(result)

